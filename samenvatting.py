# == samenvatting.py Author: Zuinige Rijder ===================================
"""
Python3 script om een samenvatting te maken van de station namen in een bestand.
"""
from copy import deepcopy
from io import TextIOWrapper
import json
import logging
import logging.config
import re
import sys
from os import path
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import Union
from dateutil import parser
from utils import (
    arg_has,
    datetime_to_datetime_str,
    dbg,
    execute_request,
    get,
    split_on_comma,
    to_float,
    same_year,
    same_month,
    same_week,
    same_day,
)


@dataclass
class Readahead:
    """Readahead"""

    curr_split: list[str]
    next_split: list[str]
    file: TextIOWrapper = None
    file_eol: bool = False
    line: str = ""
    read_done_once: bool = False
    linecount: int = 0


@dataclass
class Totals:
    """Totals"""

    name: str = None
    current_day: datetime = None
    elapsed_hours: int = 1
    pm10_kal_avg: float = None
    pm10_kal_min: float = None
    pm10_kal_max: float = None
    pm25_kal_avg: float = None
    pm25_kal_min: float = None
    pm25_kal_max: float = None
    who_pm10_daily: int = 0
    eu_pm10_daily: int = 0
    who_pm25_daily: int = 0


@dataclass
class GrandTotals:
    """GrandTotals"""

    day: Totals
    week: Totals
    month: Totals
    year: Totals


@dataclass
class KmlData:
    """KmlData"""

    output_file: TextIOWrapper = None
    max_lat: float = None
    max_lon: float = None
    min_lat: float = None
    min_lon: float = None


D = arg_has("debug")

SCRIPT_DIRNAME = path.abspath(path.dirname(__file__))
logging.config.fileConfig(f"{SCRIPT_DIRNAME}/logging_config.ini")
if D:
    logging.getLogger().setLevel(logging.DEBUG)


# keep track of WHO and EU limits
# PM10  WHO annual=15 and daily=45 (max 4x) EU annual=40 daily=50 (max 35x)
# PM2.5 WHO annual=5  and daily=15 (max 4x) EU annual=25
WHO_PM10_ANNUAL_AVG = 15
WHO_PM10_DAILY_LIMIT = 45
WHO_PM10_DAILY_COUNT = 4

WHO_PM25_ANNUAL_AVG = 5
WHO_PM25_DAILY_LIMIT = 15
WHO_PM25_DAILY_COUNT = 4

EU_PM10_ANNUAL_AVG = 40
EU_PM10_DAILY_LIMIT = 50
EU_PM10_DAILY_COUNT = 35

EU_PM25_ANNUAL_AVG = 25

# parameters
UUR = arg_has("uur")
DAY = arg_has("dag")
WEEK = arg_has("week")
MONTH = arg_has("maand")
YEAR = True  # default year

# indexes to splitted input csv items
DT = 0  # datetime
PM10_KAL = 1
PM10 = 2
PM25_KAL = 3
PM25 = 4
RH = 5
TEMP = 6

# globals
KML = KmlData()
STATION_NAME: str = ""
READAHEAD = Readahead([], [])
GRAND_TOTALS: GrandTotals = GrandTotals(None, None, None, None)
YEARLY_GRAND_TOTALS: dict[str, Totals] = {}

KEYWORD_LIST = [
    "uur",
    "dag",
    "week",
    "maand",
    "help",
    "debug",
]

# only generate summary until this year, default till current year
UNTIL_YEAR = datetime.now().strftime("%Y")

KEYWORD_ERROR = False
STATION_NAME_LIST = ""
for kindex in range(1, len(sys.argv)):
    if sys.argv[kindex].lower() not in KEYWORD_LIST:
        arg = sys.argv[kindex]
        if len(arg) == 4 and arg.isnumeric():
            UNTIL_YEAR = f"{arg}"
        elif STATION_NAME_LIST != "":
            print("Onbekende parameter: " + arg)
            KEYWORD_ERROR = True
        else:
            STATION_NAME_LIST = arg

if STATION_NAME_LIST == "" or not Path(STATION_NAME_LIST).is_file():
    print(f"Onbekend invoer bestand: {STATION_NAME_LIST}")
    KEYWORD_ERROR = True


if len(sys.argv) < 2 or KEYWORD_ERROR or arg_has("help"):
    print(
        """
Gebruik  : python samenvatting.py [uur] [dag] [week] [maand] [jjjj] STATION_LIJST.txt
Voorbeeld: python samenvatting.py _heusden.txt

Opm.1: Wilt u alleen tot en met een bepaald jaar een samenvatting hebben,
       kunt u parameter jjjj gebruiken, bijvoorbeeld 2022
Opm.2: Wilt u alle details zien, gebruik parameter uur/dag/week/maand
Opm.3: station namen van een gemeente kan opgevraagd worden met tool:
            python gemeente_station_namen.py gemeente_code
Opm.4: Voordat dit script gedraaid wordt, moeten de .csv bestanden voor
       deze STATION_LIJST.txt gegenereerd zijn met:
            python station_data_naar_csv.py STATION_LIJST.txt
    """
    )
    sys.exit(-1)


def init(current_day: datetime, split: list[str]) -> Totals:
    """init Totals with initial values"""
    _ = D and dbg(f"init({current_day})")
    pm10_kal = get_kal_float(PM10_KAL, split)
    pm25_kal = get_kal_float(PM25_KAL, split)
    totals = Totals(
        "unknown",
        current_day,
        1,
        pm10_kal,
        pm10_kal,
        pm10_kal,
        pm25_kal,
        pm25_kal,
        pm25_kal,
        0,
        0,
        0,
    )
    return totals


def deepcopy_totals(name: str, current_day_values: Totals) -> Totals:
    """deepcopy_totals"""
    result = deepcopy(current_day_values)
    result.name = name
    return result


def kml_writeln(line: str) -> None:
    """kml_writeln"""
    KML.output_file.write(line)
    KML.output_file.write("\n")


def kml_write_coordinates(lat: float, lon: float) -> None:
    """kml_write_coordinates"""
    kml_writeln(f"<Point><coordinates>{lat}, {lon}</coordinates></Point>")


def get_write_kml_coordinates(name: str) -> None:
    """get_write_kml_coordinates"""
    url = f"https://api-samenmeten.rivm.nl/v1.0/Things?$filter=name%20eq%20%27{name}%27"  # noqa
    station_data = json.loads(execute_request(url))
    array = get(station_data, "value", f"Geen station {name}")
    if len(array) == 0:
        raise ValueError(f"Geen station data gevonden voor {name}")
    if len(array) != 1:
        raise ValueError(f"Teveel station data gevonden: {array}")
    location_url = get(
        array[0],
        "Locations@iot.navigationLink",
        f"Station locatie bestaat niet {array[0]}",
    )
    station_location_data = json.loads(execute_request(location_url))
    array = get(station_location_data, "value", "Geen station locatie data")
    if len(array) == 0:
        raise ValueError("Geen station data gevonden voor {name}")
    if len(array) != 1:
        raise ValueError(f"Teveel station data gevonden: {array}")
    location = get(array[0], "location", f"Geen locatie gevonden {array}")
    coordinates = get(location, "coordinates", f"Geen coordinaten gevonden {location}")
    if len(coordinates) != 2:
        raise ValueError(f"Geen goede coordinaten gevonden: {coordinates}")
    lat = coordinates[0]
    lon = coordinates[1]
    kml_write_coordinates(lat, lon)
    if KML.max_lat is None or lat > KML.max_lat:
        KML.max_lat = lat
    if KML.min_lat is None or lat < KML.min_lat:
        KML.min_lat = lat
    if KML.min_lon is None or lat > KML.min_lon:
        KML.max_lon = lon
    if KML.min_lon is None or lat < KML.min_lon:
        KML.min_lon = lon


def klm_write_placemark(
    name: str, lat: Union[float, None] = None, lon: Union[float, None] = None
) -> None:
    """klm_write_placemark"""
    kml_writeln("<Placemark>")
    if lat and lon:
        kml_write_coordinates(lat, lon)
    else:
        get_write_kml_coordinates(name)
    kml_writeln("<description>")
    kml_writeln(f"{name}\nJaar PM10/PM2.5 (dagen) #WHO Daglimiet PM10/PM2.5")


def kml_write_name(year: Totals, name: str, home: bool = False) -> None:
    """kml_write_name"""
    if not year:
        kml_writeln(f"<name>{name}</name><styleUrl>#homeOkStyle</styleUrl>")
        return  # nothing further to do, no data UNTIL_YEAR
    elapsed_hours = max(year.elapsed_hours, 1)
    pm10_kal_avg = year.pm10_kal_avg / elapsed_hours
    pm25_kal_avg = year.pm25_kal_avg / elapsed_hours
    who_exceeded_pm10 = (
        year.pm10_kal_avg > WHO_PM10_ANNUAL_AVG
        or year.who_pm10_daily > WHO_PM10_DAILY_LIMIT
    )
    who_exceeded_pm25 = (
        pm25_kal_avg > WHO_PM25_ANNUAL_AVG or year.who_pm25_daily > WHO_PM25_DAILY_LIMIT
    )
    who_exceeded = who_exceeded_pm10 or who_exceeded_pm25
    number_of_days = int(year.elapsed_hours / 24)
    kml_writeln(
        f"<name>{pm10_kal_avg:.0f}/{pm25_kal_avg:.0f} ({number_of_days}d)</name>"  # noqa
    )  # noqa
    if home:
        if who_exceeded:
            style = "homeTooHighStyle"
        else:
            style = "homeOkStyle"
    else:
        if who_exceeded:
            style = "tooHighStyle"
        else:
            style = "okStyle"
    kml_writeln(f"<styleUrl>#{style}</styleUrl>")


COLUMN_WIDTHS = [11, 9, 10, 5, 4, 4, 4, 3, 3, 5, 4, 4, 3, 3, 1]


def format_output(output: str) -> str:
    """format_output"""
    total_line = ""
    split = split_on_comma(output)
    for i in range(len(split)):  # pylint:disable=consider-using-enumerate
        if i > 0:
            total_line += ", "
        string = split[i]
        if len(string) > COLUMN_WIDTHS[i]:
            COLUMN_WIDTHS[i] = len(string)
        if i > 12:
            text = string.ljust(COLUMN_WIDTHS[i])
        else:
            text = string.rjust(COLUMN_WIDTHS[i])
        total_line += text
    return total_line


def print_output_formatted(output: str) -> None:
    """print_output_formatted"""
    total_line = format_output(output)
    print(total_line)


def get_header() -> str:
    """get_header"""
    output = "Station, Periode, Datum, Info, PM10,(Min, Max, #WHO, #EU), PM2.5, (Min, Max, #WHO), Commentaar"  # noqa
    output = format_output(output)
    return output


def print_header() -> None:
    """print header"""
    output = get_header()
    print(output)


def get_next_csv_line() -> str:
    """
    get_next_csv_line

    Returns empty string if EOF
    Can also be called when already EOF encountered (again empty line returned)
    Skips empty lines
    Skips header lines
    Skips lines without ,
    Skips identical lines
    Skips identical lines, where only the datetime is different
    Does fill CSV_READ_AHEAD_LINE (for external use)
    """
    while not READAHEAD.file_eol:
        if READAHEAD.read_done_once:  # read 1 line
            line = READAHEAD.line
            READAHEAD.curr_split = READAHEAD.next_split
        else:  # read 2 lines
            READAHEAD.read_done_once = True
            line = READAHEAD.file.readline()
            READAHEAD.curr_split = split_on_comma(line)

        READAHEAD.linecount += 1
        READAHEAD.line = READAHEAD.file.readline()
        READAHEAD.next_split = split_on_comma(READAHEAD.line)
        if not line:
            READAHEAD.file_eol = True
            READAHEAD.line = line
            READAHEAD.next_split = []
            break  # finished

        if line != READAHEAD.line:  # skip identical lines
            line = line.strip()
            # only lines with content (starts with year 20yy)
            if line.startswith("20") and len(line) > 4 and line[:4] <= UNTIL_YEAR:
                index = line.find(",")
                next_line = READAHEAD.line.strip()
                read_ahead_index = next_line.find(",")
                # skip identical lines, when only first column (datetime) is the same
                if index >= 0 and (
                    read_ahead_index < 0 or next_line[read_ahead_index:] != line[index:]
                ):
                    _ = D and dbg(f"next=[{line}]")
                    return line

        _ = D and dbg(f"skip=[{line}]")

    _ = D and dbg("return=[]\n")
    return ""


def get_corrected_next_csv_line() -> str:
    """get_corrected_next_csv_line"""
    while True:
        line = get_next_csv_line()
        if line == "":  # EOF
            return ""  # finished

        split = READAHEAD.curr_split
        if len(split) != 7:
            _ = D and dbg(f"#### Skipping line {READAHEAD.linecount}: [{line}]")
            continue

        _ = D and dbg(str(READAHEAD.linecount) + ": LINE=[" + line + "]")
        next_line = READAHEAD.line.strip()
        next_split = READAHEAD.next_split
        if len(next_split) != 7:
            _ = D and dbg(f"Next split skip: {READAHEAD.linecount}: [{next_line}]")
            return line

        return line


def get_comment(
    prefix_starts_with_year: bool,
    t_pm10_kal_avg: float,
    t_pm25_kal_avg: float,
    year: Totals,
) -> str:
    """get_comment"""
    pm10_warnings = "PM10  "
    pm25_warnings = "PM2.5 "
    if prefix_starts_with_year:
        # year violations
        if t_pm10_kal_avg > WHO_PM10_ANNUAL_AVG:
            pm10_warnings += f"> WHO jaar {WHO_PM10_ANNUAL_AVG} "
        if t_pm25_kal_avg > WHO_PM25_ANNUAL_AVG:
            pm25_warnings += f"> WHO jaar {WHO_PM25_ANNUAL_AVG} "
        if t_pm10_kal_avg > EU_PM10_ANNUAL_AVG:
            pm10_warnings += f"> EU jaar {EU_PM10_ANNUAL_AVG} "
        if t_pm25_kal_avg > EU_PM25_ANNUAL_AVG:
            pm25_warnings += f"> EU jaar {EU_PM25_ANNUAL_AVG} "

    # daily count violations (only add when no year violations)
    if not prefix_starts_with_year or pm10_warnings == "PM10  ":
        if year.who_pm10_daily > WHO_PM10_DAILY_COUNT:
            pm10_warnings += f"> WHO dag #{year.who_pm10_daily} "
        if year.eu_pm10_daily > EU_PM10_DAILY_COUNT:
            pm10_warnings += f"> EU dag #{year.eu_pm10_daily} "

    if not prefix_starts_with_year or pm25_warnings == "PM2.5 ":
        if year.who_pm25_daily > WHO_PM25_DAILY_COUNT:
            pm25_warnings += f"> WHO dag #{year.who_pm25_daily} "

    result = ""
    if pm10_warnings != "PM10  ":
        result += pm10_warnings.strip()
        result += "; "
    if pm25_warnings != "PM2.5 ":
        result += pm25_warnings.strip()
    return result


def print_summary(prefix: str, values: Totals, year: Totals) -> None:
    """print_summary"""
    if D:
        dbg("print_summary")
        dbg("PREV  : " + str(values))
        dbg("VALUES: " + str(values))

    t_elapsed_hours = max(values.elapsed_hours, 1)
    t_pm10_kal_avg = values.pm10_kal_avg / t_elapsed_hours
    t_pm25_kal_avg = values.pm25_kal_avg / t_elapsed_hours

    if prefix.startswith("DAG "):
        _ = D and dbg(f"year: {year}")
        if t_pm10_kal_avg > WHO_PM10_DAILY_LIMIT:
            year.who_pm10_daily += 1
        if t_pm10_kal_avg > EU_PM10_DAILY_LIMIT:
            year.eu_pm10_daily += 1
        if t_pm25_kal_avg > WHO_PM25_DAILY_LIMIT:
            year.who_pm25_daily += 1
        if not DAY:
            return  # nothing to print

    output = f"{STATION_NAME},{prefix}, {t_pm10_kal_avg:.0f}, {values.pm10_kal_min:.0f}, {values.pm10_kal_max:.0f}, {year.who_pm10_daily}, {year.eu_pm10_daily}, {t_pm25_kal_avg:.0f}, {values.pm25_kal_min:.0f}, {values.pm25_kal_max:.0f}, {year.who_pm25_daily},"  # noqa

    prefix_starts_with_year = prefix.startswith("JAAR")
    if prefix_starts_with_year:
        # keep track of overall yearly GrandTotals
        splitted_prefix = prefix.split(",")
        if len(splitted_prefix) == 3:
            year_str = splitted_prefix[2].strip()
            if year_str in YEARLY_GRAND_TOTALS:
                totals = YEARLY_GRAND_TOTALS[year_str]
                totals.current_day = min(totals.current_day, values.current_day)
                totals.elapsed_hours += values.elapsed_hours
                totals.pm10_kal_avg += values.pm10_kal_avg
                totals.pm10_kal_min = min(totals.pm10_kal_min, values.pm10_kal_min)
                totals.pm10_kal_max = max(totals.pm10_kal_max, values.pm10_kal_max)
                totals.pm25_kal_avg += values.pm25_kal_avg
                totals.pm25_kal_min = min(totals.pm25_kal_min, values.pm25_kal_min)
                totals.pm25_kal_max = max(totals.pm25_kal_max, values.pm25_kal_max)

                totals.who_pm10_daily = max(
                    totals.who_pm10_daily, values.who_pm10_daily
                )
                totals.eu_pm10_daily = max(totals.eu_pm10_daily, values.eu_pm10_daily)
                totals.who_pm25_daily = max(
                    totals.who_pm25_daily, values.who_pm25_daily
                )
            else:
                YEARLY_GRAND_TOTALS[year_str] = deepcopy_totals(year_str, year)

        elapsed_hours = max(year.elapsed_hours, 1)
        pm10_kal_avg = year.pm10_kal_avg / elapsed_hours
        pm25_kal_avg = year.pm25_kal_avg / elapsed_hours
        number_of_days = int(year.elapsed_hours / 24)
        kml_writeln(
            f'{year.current_day.strftime("%Y"):4s} {pm10_kal_avg:.0f}/{pm25_kal_avg:.0f} ({number_of_days}d) #{year.who_pm10_daily}/{year.who_pm25_daily}'  # noqa
        )
        comment = get_comment(prefix_starts_with_year, pm10_kal_avg, pm25_kal_avg, year)
        output += comment
        if comment != "":
            comment = comment.replace("; ", "\n     ")
            kml_writeln(f"     {comment}")
    else:
        comment = get_comment(
            prefix_starts_with_year, t_pm10_kal_avg, t_pm25_kal_avg, year
        )
        output += comment
    print_output_formatted(output)


def print_summaries(current_day_values: Totals, last: bool) -> None:
    """print_summaries"""
    current_day = current_day_values.current_day
    day_str = GRAND_TOTALS.day.current_day.strftime("%Y-%m-%d")

    if not same_day(current_day, GRAND_TOTALS.day.current_day) or last:
        day_info = GRAND_TOTALS.day.current_day.strftime("%a")
        print_summary(
            f"DAG     , {day_str}, {day_info}",
            GRAND_TOTALS.day,
            GRAND_TOTALS.year,
        )
        GRAND_TOTALS.day = deepcopy_totals("day", current_day_values)

    if WEEK and (not same_week(current_day, GRAND_TOTALS.week.current_day) or last):
        weeknr = GRAND_TOTALS.week.current_day.strftime("%W")
        print_summary(
            f"WEEK    , {day_str}, WK {weeknr}",
            GRAND_TOTALS.week,
            GRAND_TOTALS.year,
        )
        GRAND_TOTALS.week = deepcopy_totals("week", current_day_values)

    if MONTH and (not same_month(current_day, GRAND_TOTALS.month.current_day) or last):
        month_info = GRAND_TOTALS.month.current_day.strftime("%b")
        print_summary(
            f"MAAND   , {day_str}, {month_info}",
            GRAND_TOTALS.month,
            GRAND_TOTALS.year,
        )
        GRAND_TOTALS.month = deepcopy_totals("month", current_day_values)

    if not same_year(current_day, GRAND_TOTALS.year.current_day) or last:
        year = GRAND_TOTALS.year.current_day.strftime("%Y")
        number_of_days = int(GRAND_TOTALS.year.elapsed_hours / 24)
        if YEAR:
            print_summary(
                f"JAAR {number_of_days:3d}d, {day_str}, {year}",
                GRAND_TOTALS.year,
                GRAND_TOTALS.year,
            )
        if DAY:
            print_summary(
                f"DAGGEM  , {day_str}, {number_of_days}d ",
                GRAND_TOTALS.year,
                GRAND_TOTALS.year,
            )
        if WEEK:
            print_summary(
                f"WEEKGEM , {day_str}, {number_of_days}d ",
                GRAND_TOTALS.year,
                GRAND_TOTALS.year,
            )

        if MONTH:
            print_summary(
                f"MAANDGEM, {day_str}, {number_of_days}d ",
                GRAND_TOTALS.year,
                GRAND_TOTALS.year,
            )

        if not last:
            GRAND_TOTALS.year = deepcopy_totals("year", current_day_values)


def keep_track_of_totals(split: list[str]) -> None:
    """keep_track_of_totals"""
    if D:
        dbg("keep track of totals")
        dbg("     split: " + str(split))
        dbg("    before: " + str(GRAND_TOTALS))

    pm10_kal = get_kal_float(PM10_KAL, split)
    if pm10_kal < 0.0:
        return  # skip uncalibrated values
    pm25_kal = get_kal_float(PM25_KAL, split)
    if pm25_kal < 0.0:
        return  # skip uncalibrated values

    # update day totals
    GRAND_TOTALS.day.elapsed_hours += 1
    GRAND_TOTALS.day.pm10_kal_avg += pm10_kal
    GRAND_TOTALS.day.pm25_kal_avg += pm25_kal

    GRAND_TOTALS.day.pm10_kal_min = min(pm10_kal, GRAND_TOTALS.day.pm10_kal_min)
    GRAND_TOTALS.day.pm10_kal_max = max(pm10_kal, GRAND_TOTALS.day.pm10_kal_max)

    GRAND_TOTALS.day.pm25_kal_min = min(pm25_kal, GRAND_TOTALS.day.pm25_kal_min)
    GRAND_TOTALS.day.pm25_kal_max = max(pm25_kal, GRAND_TOTALS.day.pm25_kal_max)

    # update week totals
    if WEEK:
        GRAND_TOTALS.week.elapsed_hours += 1
        GRAND_TOTALS.week.pm10_kal_avg += pm10_kal
        GRAND_TOTALS.week.pm25_kal_avg += pm25_kal

        GRAND_TOTALS.week.pm10_kal_min = min(pm10_kal, GRAND_TOTALS.week.pm10_kal_min)
        GRAND_TOTALS.week.pm10_kal_max = max(pm10_kal, GRAND_TOTALS.week.pm10_kal_max)

        GRAND_TOTALS.week.pm25_kal_min = min(pm25_kal, GRAND_TOTALS.week.pm25_kal_min)
        GRAND_TOTALS.week.pm25_kal_max = max(pm25_kal, GRAND_TOTALS.week.pm25_kal_max)

    # update month totals
    if MONTH:
        GRAND_TOTALS.month.elapsed_hours += 1
        GRAND_TOTALS.month.pm10_kal_avg += pm10_kal
        GRAND_TOTALS.month.pm25_kal_avg += pm25_kal

        GRAND_TOTALS.month.pm10_kal_min = min(pm10_kal, GRAND_TOTALS.month.pm10_kal_min)
        GRAND_TOTALS.month.pm10_kal_max = max(pm10_kal, GRAND_TOTALS.month.pm10_kal_max)

        GRAND_TOTALS.month.pm25_kal_min = min(pm25_kal, GRAND_TOTALS.month.pm25_kal_min)
        GRAND_TOTALS.month.pm25_kal_max = max(pm25_kal, GRAND_TOTALS.month.pm25_kal_max)

    # update year totals
    GRAND_TOTALS.year.elapsed_hours += 1
    GRAND_TOTALS.year.pm10_kal_avg += pm10_kal
    GRAND_TOTALS.year.pm25_kal_avg += pm25_kal

    GRAND_TOTALS.year.pm10_kal_min = min(pm10_kal, GRAND_TOTALS.year.pm10_kal_min)
    GRAND_TOTALS.year.pm10_kal_max = max(pm10_kal, GRAND_TOTALS.year.pm10_kal_max)

    GRAND_TOTALS.year.pm25_kal_min = min(pm25_kal, GRAND_TOTALS.year.pm25_kal_min)
    GRAND_TOTALS.year.pm25_kal_max = max(pm25_kal, GRAND_TOTALS.year.pm25_kal_max)

    if D:
        current_day = parser.parse(split[DT])
        print(
            f"{int(GRAND_TOTALS.year.elapsed_hours/24)} {current_day} year.elapsed_hours: {GRAND_TOTALS.year.elapsed_hours}"  # noqa
        )
    _ = D and dbg("     after: " + str(GRAND_TOTALS))


def get_kal_float(index, split) -> float:
    """get_kal_float"""
    value = ""
    if len(split) >= index - 1:
        value = split[index].strip()
    if value == "":
        value = "-1.0"
    return to_float(value)


def handle_line(
    linecount: int,
    split: list[str],
    prev_split: list[str],
    last: bool,
) -> None:
    """handle_line"""
    _ = D and dbg(f"handle_line: {split}, {prev_split}")

    current_day = parser.parse(split[DT])
    if not GRAND_TOTALS.day:
        _ = D and dbg(
            f"not TDAY: {GRAND_TOTALS.day} first time, fill in with initial values"
        )
        values = init(current_day, split)
        if values.pm10_kal_avg < 0.0 or values.pm25_kal_avg < 0.0:
            return  # no calibrated value yet
        GRAND_TOTALS.day = deepcopy_totals("day", values)
        GRAND_TOTALS.week = deepcopy_totals("week", values)
        GRAND_TOTALS.month = deepcopy_totals("month", values)
        GRAND_TOTALS.year = deepcopy_totals("year", values)
        return

    if split[DT] == prev_split[DT] and not last:
        _ = D and dbg(
            f"Warning: timestamp same, skipping: {linecount}\nSPLIT: {split}\nPREV : {prev_split}"  # noqa
        )
        return

    # take into account totals per line
    if not last:  # skip keep_track_of_totals for last entry
        if UUR:
            values = init(current_day, split)
            if values.pm10_kal_avg >= 0.0 and values.pm25_kal_avg >= 0.0:
                year = GRAND_TOTALS.year
                day_info = current_day.strftime("%Y-%m-%d")
                uur_info = current_day.strftime("%H:%M")
                output = f"{STATION_NAME}, UUR, {day_info}, {uur_info}, {values.pm10_kal_avg:.0f}, {year.pm10_kal_min:.0f}, {year.pm10_kal_max:.0f}, {year.who_pm10_daily}, {year.eu_pm10_daily}, {values.pm25_kal_avg:.0f}, {year.pm25_kal_min:.0f}, {year.pm25_kal_max:.0f}, {year.who_pm25_daily},"  # noqa
                output += get_comment(
                    False, values.pm10_kal_avg, values.pm25_kal_avg, year
                )
                print_output_formatted(output)

        keep_track_of_totals(split)

    if last or not same_day(current_day, GRAND_TOTALS.day.current_day):
        _ = D and dbg(f"DAY change: {GRAND_TOTALS.day}")
        print_summaries(init(current_day, split), last)

    return


def summary() -> None:
    """summary of monitor.csv file"""
    prev_line: str = ""
    prev_split: list[str] = []
    GRAND_TOTALS.day = None
    GRAND_TOTALS.week = None
    GRAND_TOTALS.month = None
    GRAND_TOTALS.year = None

    while True:
        line = get_corrected_next_csv_line()
        if line == "":  # EOF
            break  # finish loop
        _ = D and dbg(str(READAHEAD.linecount) + ": LINE=[" + line + "]")
        split = READAHEAD.curr_split
        handle_line(READAHEAD.linecount, split, prev_split, False)

        prev_line = line
        prev_split = split

    # also compute last last day/week/month
    _ = D and dbg("Handling last values")
    # handle end of day for last value
    eod_line = prev_line[0:11] + "23:59" + prev_line[16:]
    last_split = split_on_comma(eod_line)
    _ = D and dbg(
        f"prev_line: {prev_line}\n eod_line: {eod_line}\n{prev_split}\n{last_split}"
    )
    if prev_line != "":
        handle_line(READAHEAD.linecount, last_split, prev_split, False)
        # and show summaries
        handle_line(READAHEAD.linecount, last_split, last_split, True)


def handle_station_list(station_name_list: str) -> None:
    """handle_station_list"""
    global STATION_NAME, READAHEAD  # pylint:disable=global-statement
    input_file = Path(station_name_list)
    if not input_file.is_file():
        raise ValueError(f"{station_name_list} invoer bestand bestaat niet")
    print_header()
    with input_file.open("r", encoding="utf-8") as file:
        for name in file:
            name = re.sub("#.*", "", name)
            name = name.strip()
            if name != "":
                STATION_NAME = name
                input_csv_file = Path(name + ".csv")
                if not input_csv_file.is_file():
                    raise ValueError(f"FOUT: bestand bestaat niet: {input_csv_file}")
                _ = D and dbg(f"Samenvatting genereren uit {input_csv_file}")

                READAHEAD = Readahead([], [])
                READAHEAD.file = input_csv_file.open("r", encoding="utf-8")

                klm_write_placemark(name)

                summary()  # do the work

                kml_writeln("</description>")
                kml_write_name(GRAND_TOTALS.year, name)
                kml_writeln("</Placemark>")
                READAHEAD.file.close()
                print()

    keys = list(YEARLY_GRAND_TOTALS.keys())
    keys.sort()
    sorted_yearly = {i: YEARLY_GRAND_TOTALS[i] for i in keys}
    kml_writeln("<Placemark>")
    # just put the overall somewhere in the middle of the coordinates
    klm_write_placemark(
        station_name_list,
        (KML.max_lat + KML.min_lat) / 2,
        (KML.max_lon + KML.min_lon) / 2,
    )
    for key, yearly in sorted_yearly.items():
        elapsed_hours = max(yearly.elapsed_hours, 1)
        pm10_kal_avg = yearly.pm10_kal_avg / elapsed_hours
        pm25_kal_avg = yearly.pm25_kal_avg / elapsed_hours
        day_str = yearly.current_day.strftime("%Y-%m-%d")
        output = f"Gemiddelde,JAAR,{day_str},{key},{pm10_kal_avg:.0f}, {yearly.pm10_kal_min:.0f}, {yearly.pm10_kal_max:.0f}, {yearly.who_pm10_daily}, {yearly.eu_pm10_daily}, {pm25_kal_avg:.0f}, {yearly.pm25_kal_min:.0f}, {yearly.pm25_kal_max:.0f}, {yearly.who_pm25_daily},"  # noqa
        comment = get_comment(True, pm10_kal_avg, pm25_kal_avg, yearly)
        output += comment
        print_output_formatted(output)
        number_of_days = int(yearly.elapsed_hours / 24)
        kml_writeln(
            f'{yearly.current_day.strftime("%Y"):4s} {pm10_kal_avg:.0f}/{pm25_kal_avg:.0f} ({number_of_days}d) #{yearly.who_pm10_daily}/{yearly.who_pm25_daily}'  # noqa
        )
        if comment != "":
            comment = comment.replace("; ", "\n     ")
            kml_writeln(f"     {comment}")

    kml_writeln("</description>")
    last_year = YEARLY_GRAND_TOTALS[keys[-1]]
    kml_write_name(last_year, station_name_list, True)
    kml_writeln("</Placemark>")


with Path(f"{STATION_NAME_LIST}.kml").open("w", encoding="utf-8") as KML.output_file:
    now_str = datetime_to_datetime_str(datetime.now())
    kml_writeln(
        """
<?xml version="1.0" encoding="UTF-8"?>
<kml xmlns="http://www.opengis.net/kml/2.2">
<Document>
<Style id="homeOkStyle"><IconStyle><Icon>
    <href>https://maps.google.com/mapfiles/kml/shapes/ranger_station.png</href></Icon></IconStyle></Style>
<Style id="homeTooHighStyle"><IconStyle><Icon>
    <href>https://maps.google.com/mapfiles/kml/shapes/schools.png</href></Icon></IconStyle></Style>
<Style id="tooHighStyle"><IconStyle><Icon>
    <href>https://maps.google.com/mapfiles/kml/shapes/firedept.png</href></Icon></IconStyle></Style>
<Style id="okStyle"><IconStyle><Icon>
    <href>https://maps.google.com/mapfiles/kml/shapes/parks.png</href></Icon></IconStyle></Style>
    """
    )
    kml_writeln(f"<name>{STATION_NAME_LIST} {now_str}</name>")

    handle_station_list(STATION_NAME_LIST)

    kml_writeln("</Document>")
    kml_writeln("</kml>")
