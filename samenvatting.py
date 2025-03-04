# == samenvatting.py Author: Zuinige Rijder ===================================
"""
Python3 script om een samenvatting te maken van de station namen in een bestand.
"""
# pylint:disable=too-many-lines
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
import locale
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
    pm25_kalibration_factor: float = None
    pm10_kalibration_factor: float = None


@dataclass
class Totals:
    """Totals"""

    name: str = None
    current_day: datetime = None
    elapsed_seconds_pm10: int = 3600
    elapsed_seconds_pm25: int = 3600
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
    all_years: Totals


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

locale.setlocale(locale.LC_TIME, "nl_NL.UTF-8")

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
PM10_KAL_FACTOR = 7
PM25_KAL_FACTOR = 8

# globals
KML = KmlData()
STATION_NAME: str = ""
STATION_NAME_KML_PRINTED = True
READAHEAD = Readahead([], [])
GRAND_TOTALS: GrandTotals = GrandTotals(None, None, None, None, None)
AVERAGE_GRAND_TOTALS: dict[str, Totals] = {}

# PM2.5 AND PM10 dictionary for writing at the end the PM2.5 and PM10 .csv files
PM25_DICT: dict[str, str] = {}
PM10_DICT: dict[str, str] = {}
YEARS_DICT: dict[int, str] = {}

KEYWORD_LIST = [
    "uur",
    "dag",
    "week",
    "maand",
    "help",
    "debug",
]

KEYWORD_ERROR = False
STATION_NAME_LIST = ""

# filters
YEAR_FROM = 2000
YEAR_UNTIL = 3000
YEAR_FILTER = False
MONTH_FROM = 1
MONTH_UNTIL = 12
HOUR_FROM = 0
HOUR_UNTIL = 23
WEEKDAY_FROM = 1
WEEKDAY_UNTIL = 7
year_filter_regex = re.compile(r"^j(\d+)-(\d+)$")
month_filter_regex = re.compile(r"^m(\d+)-(\d+)$")
hour_filter_regex = re.compile(r"^u(\d+)-(\d+)$")
weekday_filter_regex = re.compile(r"^d(\d+)-(\d+)$")
for kindex in range(1, len(sys.argv)):
    if sys.argv[kindex].lower() not in KEYWORD_LIST:
        arg = sys.argv[kindex]
        if year_filter_regex.search(arg.lower().strip()):
            year_filter = year_filter_regex.search(arg.lower().strip())
            YEAR_FROM = int(year_filter.group(1))
            YEAR_UNTIL = int(year_filter.group(2))
            YEAR_FILTER = True
            print(
                f"Jaar filter   : {arg:12s} Van: {YEAR_FROM:5d} Tot en met: {YEAR_UNTIL:5d}"  # noqa
            )
        elif month_filter_regex.search(arg.lower().strip()):
            month_filter = month_filter_regex.search(arg.lower().strip())
            MONTH_FROM = int(month_filter.group(1))
            MONTH_UNTIL = int(month_filter.group(2))
            print(
                f"Maand filter  : {arg:12s} Van: {MONTH_FROM:5d} Tot en met: {MONTH_UNTIL:5d}"  # noqa
            )
        elif hour_filter_regex.search(arg.lower().strip()):
            hour_filter = hour_filter_regex.search(arg.lower().strip())
            HOUR_FROM = int(hour_filter.group(1))
            HOUR_UNTIL = int(hour_filter.group(2))
            print(
                f"Uur filter    : {arg:12s} Van: {HOUR_FROM:5d} Tot en met: {HOUR_UNTIL:5d}"  # noqa
            )
        elif weekday_filter_regex.search(arg.lower().strip()):
            weekday_filter = weekday_filter_regex.search(arg.lower().strip())
            WEEKDAY_FROM = int(weekday_filter.group(1))
            WEEKDAY_UNTIL = int(weekday_filter.group(2))
            print(
                f"Weekdag filter: {arg:12s} Van: {WEEKDAY_FROM:5d} Tot en met: {WEEKDAY_UNTIL:5d}"  # noqa
            )
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
Gebruik  : python samenvatting.py STATION_LIJST.txt
Uitvoer  : STATION_LIST.txt.kml          (bestand in Google My Maps formaat)
           STATION_LIST.txt.pm25.csv     (PM2.5 per jaar per station in csv formaat)
           STATION_LIST.txt.pm10.csv     (PM10  per jaar per station in csv formaat)
           STATION_LIST.txt.pm25.avg.csv (gemiddelde PM2.5 per jaar per station)
           STATION_LIST.txt.pm10.avg.csv (gemiddelde PM10  per jaar per station)
Voorbeeld: python samenvatting.py _GemeenteHeusden.txt
Opties   : [uur] [dag] [week] [maand] [j2000-3000] [m1-12] [d1-7] [u0-23]

Opm.1: Wilt u meer details zien, gebruik parameter uur/dag/week/maand
Opm.2: Wilt u alleen bepaalde jaren mee te nemen,
       kunt u filteren met optie [j2000-3000]:
       bijvoorbeeld alleen jaren 2021 tot en met 2022: j2021-2022
Opm.3: Wilt u alleen bepaalde maanden mee te nemen,
       kunt u filteren met optie [m1-12]:
       bijvoorbeeld alleen de maanden november tot en met maart: m11-3
Opm.4: Wilt u alleen bepaalde uren mee te nemen,
       kunt u filteren met optie [u0-23]:
       bijvoorbeeld alleen de uren van 18:00 tot en met 02:00: u18-2
Opm.5: Wilt u alleen bepaalde dagen mee te nemen,
       kunt u filteren met optie [d1-7]:
       1=ma, 2=di, 3=wo, 4=do, 5=vr, 6=za, 7=zo.
       Voorbeeld voor weekenden, inclusief vrijdag: d5-7
Opm.6: station namen van een gemeente kan opgevraagd worden met tool:
            python gemeente_station_namen.py gemeente_code
Opm.7: Voordat dit script gedraaid wordt, moeten de .csv bestanden voor
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
    # if one calibrated value is not filled, just overrule with the max WHO value.
    # this is the best workaround I can do for now, to use one of both calibrated values
    if pm10_kal < 0.0:
        pm10_kal = 10.0
    if pm25_kal < 0.0:
        pm25_kal = 5.0
    totals = Totals(
        name="unknown",
        current_day=current_day,
        elapsed_seconds_pm10=3600,
        elapsed_seconds_pm25=3600,
        pm10_kal_avg=pm10_kal * 3600,
        pm10_kal_min=pm10_kal,
        pm10_kal_max=pm10_kal,
        pm25_kal_avg=pm25_kal * 3600,
        pm25_kal_min=pm25_kal,
        pm25_kal_max=pm25_kal,
        who_pm10_daily=0,
        eu_pm10_daily=0,
        who_pm25_daily=0,
    )
    return totals


def deepcopy_totals(name: str, current_day_values: Totals) -> Totals:
    """deepcopy_totals"""
    result = deepcopy(current_day_values)
    result.name = name
    return result


def kml_writeln(line: str) -> None:
    """kml_writeln"""
    global STATION_NAME_KML_PRINTED  # pylint:disable=global-statement
    if not STATION_NAME_KML_PRINTED:
        STATION_NAME_KML_PRINTED = True
        klm_write_placemark(STATION_NAME)

    KML.output_file.write(line)
    KML.output_file.write("\n")


def kml_write_coordinates(lat: float, lon: float) -> None:
    """kml_write_coordinates"""
    kml_writeln(f"<Point><coordinates>{lat}, {lon}</coordinates></Point>")


def get_write_kml_coordinates(name: str) -> None:
    """get_write_kml_coordinates"""
    if name == "RICKTEST":
        name = "LTD_56607"
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
    kml_writeln(f"{name}\n")
    kml_writeln("Jaar PM10/PM2.5 (dagen) #WHO Daglimiet")
    kml_writeln("==================================\n")


def kml_write_name(year: Totals, name: str, home: bool = False) -> None:
    """kml_write_name"""
    if not year:
        kml_writeln(f"<name>{name}</name><styleUrl>#homeOkStyle</styleUrl>")
        return  # nothing further to do, no data UNTIL_YEAR
    elapsed_seconds_pm10 = year.elapsed_seconds_pm10
    elapsed_seconds_pm25 = year.elapsed_seconds_pm25
    pm10_kal_avg = year.pm10_kal_avg / elapsed_seconds_pm10
    pm25_kal_avg = year.pm25_kal_avg / elapsed_seconds_pm25
    who_exceeded_pm10 = (
        year.pm10_kal_avg > WHO_PM10_ANNUAL_AVG
        or year.who_pm10_daily > WHO_PM10_DAILY_LIMIT
    )
    who_exceeded_pm25 = (
        pm25_kal_avg > WHO_PM25_ANNUAL_AVG or year.who_pm25_daily > WHO_PM25_DAILY_LIMIT
    )
    who_exceeded = who_exceeded_pm10 or who_exceeded_pm25
    number_of_days_pm10 = int(year.elapsed_seconds_pm10 / 86400)
    number_of_days_pm25 = int(year.elapsed_seconds_pm25 / 86400)
    kml_writeln(
        f"<name>{pm10_kal_avg:.1f}/{pm25_kal_avg:.1f} ({number_of_days_pm10}d/{number_of_days_pm25}d)</name>"  # noqa
    )  # noqa
    if home:
        if who_exceeded:
            style = "homeTooHighStyle"
        else:
            style = "homeOkStyle"
    else:
        if who_exceeded:
            if pm25_kal_avg >= (WHO_PM25_ANNUAL_AVG * 1.6):  # average >= 8 PM2.5
                style = "cautionStyle"
            else:
                style = "tooHighStyle"
        else:
            style = "okStyle"
    kml_writeln(f"<styleUrl>#{style}</styleUrl>")


COLUMN_WIDTHS = [11, 19, 10, 7, 5, 4, 4, 3, 3, 5, 4, 4, 3, 3, 1]


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


def fill_pm_kal(pm_index, pm_kal_index):
    """fill_pm_kal"""
    pm_kal = get_kal_float(pm_kal_index, READAHEAD.curr_split)
    pm10_measurement = pm_kal_index == PM10_KAL
    pm_id = "PM2.5"
    if pm10_measurement:
        pm_id = "PM10"
    pm = get_kal_float(pm_index, READAHEAD.curr_split)
    if pm_kal > 0.0 and pm > 0.0:
        kalibration_factor = pm_kal / pm
        if pm10_measurement:
            READAHEAD.pm10_kalibration_factor = kalibration_factor
        else:
            READAHEAD.pm25_kalibration_factor = kalibration_factor
        if D:
            print(
                f"{READAHEAD.curr_split[DT]} New kalibration factor {pm_id} pm_kal: {pm_kal:.2f}, pm: {pm:.2f}, kalibration_factor: {kalibration_factor:.2f}"  # noqa
            )
    elif pm > 0.0:
        # interpolate
        if pm10_measurement:
            kalibration_factor = READAHEAD.pm10_kalibration_factor
        else:
            kalibration_factor = READAHEAD.pm25_kalibration_factor
        if kalibration_factor:
            pm_kal = pm * kalibration_factor
            if D:
                print(
                    f"{READAHEAD.curr_split[DT]} Interpolation {pm_id} pm_kal: {pm_kal:.2f}, pm: {pm:.2f}, kalibration_factor: {kalibration_factor:.2f}"  # noqa
                )

    if pm_kal > 0.0:
        READAHEAD.curr_split[pm_kal_index] = f"{pm_kal:.2f}"


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
        skip = False
        if READAHEAD.read_done_once:  # read 1 line
            line = READAHEAD.line
            if READAHEAD.next_split[DT] == READAHEAD.curr_split[DT]:
                # skip lines with identical timestamp
                # probably this is Summer/Winter time change
                if D:
                    print(
                        f"Warning: timestamp same, skipping: {READAHEAD.linecount} {line}\nSPLIT: {READAHEAD.next_split}\nPREV : {READAHEAD.curr_split}"  # noqa
                    )
                skip = True

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

        if (
            not skip or line != READAHEAD.line
        ):  # skip lines with identical timestamp or identical lines
            line = line.strip()
            # only lines with content (starts with year 20yy)
            if len(line) > 16 and line.startswith("20"):
                if not skip and (YEAR_FROM != 2000 or YEAR_UNTIL != 3000):
                    # filter on year
                    year = int(line[:4])
                    skip = year < YEAR_FROM or year > YEAR_UNTIL
                    if D:
                        print(
                            f"year: {year} skip: {skip} from: {YEAR_FROM} to: {YEAR_UNTIL}"  # noqa
                        )

                if not skip and (MONTH_FROM != 1 or MONTH_UNTIL != 12):
                    # filter on month
                    month = int(line[5:7])
                    if MONTH_FROM <= MONTH_UNTIL:
                        skip = month < MONTH_FROM or month > MONTH_UNTIL
                    else:
                        skip = not (month >= MONTH_FROM or month <= MONTH_UNTIL)
                    if D:
                        print(
                            f"month: {month} skip: {skip} from: {MONTH_FROM} to: {MONTH_UNTIL}"  # noqa
                        )

                if not skip and (HOUR_FROM != 0 or HOUR_UNTIL != 23):
                    # filter on hour
                    hour = int(line[11:13])
                    if HOUR_FROM <= HOUR_UNTIL:
                        skip = hour < HOUR_FROM or hour > HOUR_UNTIL
                    else:
                        skip = not (hour >= HOUR_FROM or hour <= HOUR_UNTIL)
                    if D:
                        print(
                            f"hour: {hour} skip: {skip} from: {HOUR_FROM} to: {HOUR_UNTIL}"  # noqa
                        )

                if not skip and (WEEKDAY_FROM != 0 or WEEKDAY_UNTIL != 23):
                    # filter on weekday
                    current_date = datetime.strptime(line[0:10], "%Y-%m-%d")
                    weekday = current_date.isoweekday()
                    if WEEKDAY_FROM <= WEEKDAY_UNTIL:
                        skip = weekday < WEEKDAY_FROM or weekday > WEEKDAY_UNTIL
                    else:
                        skip = not (weekday >= WEEKDAY_FROM or weekday <= WEEKDAY_UNTIL)
                    if D:
                        print(
                            f"weekday: {weekday} date: {current_date} skip: {skip} from: {WEEKDAY_FROM} to: {WEEKDAY_UNTIL}"  # noqa
                        )

                if not skip:
                    fill_pm_kal(PM10, PM10_KAL)
                    fill_pm_kal(PM25, PM25_KAL)
                    pm10_kal = get_kal_float(PM10_KAL, READAHEAD.curr_split)
                    pm25_kal = get_kal_float(PM25_KAL, READAHEAD.curr_split)
                    skip = pm10_kal < 0.0 and pm25_kal < 0.0

                if not skip:
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
        if len(split) < 7:
            _ = D and dbg(f"#### Skipping line {READAHEAD.linecount}: [{line}]")
            continue

        _ = D and dbg(str(READAHEAD.linecount) + ": LINE=[" + line + "]")
        next_line = READAHEAD.line.strip()
        next_split = READAHEAD.next_split
        if len(next_split) < 7:
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


def update_average_totals(key_str: str, values: Totals):
    """update_average_totals"""
    if D and key_str == "Alle jaren":
        print(
            f"#Before update_average_totals: key_str: {key_str}\nValues : {values}\nAverage:{AVERAGE_GRAND_TOTALS[key_str]}"  # noqa
        )
    if key_str in AVERAGE_GRAND_TOTALS:
        totals = AVERAGE_GRAND_TOTALS[key_str]
        totals.current_day = min(totals.current_day, values.current_day)
        totals.elapsed_seconds_pm10 += values.elapsed_seconds_pm10
        totals.elapsed_seconds_pm25 += values.elapsed_seconds_pm25
        totals.pm10_kal_avg += values.pm10_kal_avg
        totals.pm10_kal_min = min(totals.pm10_kal_min, values.pm10_kal_min)
        totals.pm10_kal_max = max(totals.pm10_kal_max, values.pm10_kal_max)
        totals.pm25_kal_avg += values.pm25_kal_avg
        totals.pm25_kal_min = min(totals.pm25_kal_min, values.pm25_kal_min)
        totals.pm25_kal_max = max(totals.pm25_kal_max, values.pm25_kal_max)

        totals.who_pm10_daily += values.who_pm10_daily
        totals.eu_pm10_daily += values.eu_pm10_daily
        totals.who_pm25_daily += values.who_pm25_daily
    else:
        AVERAGE_GRAND_TOTALS[key_str] = deepcopy_totals(key_str, values)
    if D:
        print(
            f"#After  update_average_totals: key_str: {key_str}\nValues : {values}\nAverage:{AVERAGE_GRAND_TOTALS[key_str]}"  # noqa
        )


def print_summary(prefix: str, values: Totals) -> None:
    """print_summary"""
    _ = D and dbg(f"print_summary: {prefix} VALUES:{values}")

    t_elapsed_seconds_pm10 = values.elapsed_seconds_pm10
    t_elapsed_seconds_pm25 = values.elapsed_seconds_pm25
    t_pm10_kal_avg = values.pm10_kal_avg / t_elapsed_seconds_pm10
    t_pm25_kal_avg = values.pm25_kal_avg / t_elapsed_seconds_pm25

    if prefix.startswith("DAG "):
        if DAY and "2022-03-23" in prefix:
            print(f"{t_pm10_kal_avg}, VALUES: {str(values)}")

        if t_pm10_kal_avg > WHO_PM10_DAILY_LIMIT:
            GRAND_TOTALS.year.who_pm10_daily += 1
            GRAND_TOTALS.month.who_pm10_daily += 1
            GRAND_TOTALS.week.who_pm10_daily += 1
            GRAND_TOTALS.day.who_pm10_daily += 1
        if t_pm10_kal_avg > EU_PM10_DAILY_LIMIT:
            GRAND_TOTALS.year.eu_pm10_daily += 1
            GRAND_TOTALS.month.eu_pm10_daily += 1
            GRAND_TOTALS.week.eu_pm10_daily += 1
            GRAND_TOTALS.day.eu_pm10_daily += 1
        if t_pm25_kal_avg > WHO_PM25_DAILY_LIMIT:
            # print(
            #    f"t_pm25_kal_avg={t_pm25_kal_avg}>{WHO_PM25_DAILY_LIMIT}, {prefix}, {GRAND_TOTALS.year}"  # noqa
            # )
            GRAND_TOTALS.year.who_pm25_daily += 1
            GRAND_TOTALS.month.who_pm25_daily += 1
            GRAND_TOTALS.week.who_pm25_daily += 1
            GRAND_TOTALS.day.who_pm25_daily += 1
        if not DAY:
            return  # nothing to print

    output = f"{STATION_NAME},{prefix}, {t_pm10_kal_avg:.1f}, {values.pm10_kal_min:.0f}, {values.pm10_kal_max:.0f}, {values.who_pm10_daily}, {values.eu_pm10_daily}, {t_pm25_kal_avg:.1f}, {values.pm25_kal_min:.0f}, {values.pm25_kal_max:.0f}, {values.who_pm25_daily},"  # noqa

    if prefix.startswith("JAAR"):
        elapsed_seconds_pm10 = GRAND_TOTALS.year.elapsed_seconds_pm10
        elapsed_seconds_pm25 = GRAND_TOTALS.year.elapsed_seconds_pm25
        pm10_kal_avg = GRAND_TOTALS.year.pm10_kal_avg / elapsed_seconds_pm10
        pm25_kal_avg = GRAND_TOTALS.year.pm25_kal_avg / elapsed_seconds_pm25
        number_of_days_pm10 = int(GRAND_TOTALS.year.elapsed_seconds_pm10 / 86400)
        number_of_days_pm25 = int(GRAND_TOTALS.year.elapsed_seconds_pm25 / 86400)
        year = f'{GRAND_TOTALS.year.current_day.strftime("%Y"):4s}'
        kml_writeln(
            f"{year}    {pm10_kal_avg:.1f}/{pm25_kal_avg:.1f} ({number_of_days_pm10}d/{number_of_days_pm25}d) #{GRAND_TOTALS.year.who_pm10_daily}/{GRAND_TOTALS.year.who_pm25_daily}"  # noqa
        )
        comment = get_comment(True, pm10_kal_avg, pm25_kal_avg, GRAND_TOTALS.year)
        output += comment
        if comment != "":
            comment = comment.replace("; ", "\n")
            kml_writeln(f"{comment}\n")

        # keep track of station/years/PM2.5/PM10
        PM25_DICT[f"{STATION_NAME},{year}"] = (
            f"{GRAND_TOTALS.year.pm25_kal_avg:.1f},{elapsed_seconds_pm25}"
        )
        PM10_DICT[f"{STATION_NAME},{year}"] = (
            f"{GRAND_TOTALS.year.pm10_kal_avg:.1f},{elapsed_seconds_pm10}"
        )
        YEARS_DICT[year] = True

    elif prefix.startswith("ALLES"):
        elapsed_seconds_pm10 = values.elapsed_seconds_pm10
        elapsed_seconds_pm25 = values.elapsed_seconds_pm25
        pm10_kal_avg = values.pm10_kal_avg / elapsed_seconds_pm10
        pm25_kal_avg = values.pm25_kal_avg / elapsed_seconds_pm25
        number_of_days_pm10 = int(values.elapsed_seconds_pm10 / 86400)
        number_of_days_pm25 = int(values.elapsed_seconds_pm25 / 86400)
        kml_writeln(
            f"Gem.   {pm10_kal_avg:.1f}/{pm25_kal_avg:.1f} ({number_of_days_pm10}d/{number_of_days_pm25}d) #{values.who_pm10_daily}/{values.who_pm25_daily}"  # noqa
        )
        comment = get_comment(True, pm10_kal_avg, pm25_kal_avg, values)
        output += comment
        if comment != "":
            comment = comment.replace("; ", "\n")
            kml_writeln(f"{comment}\n")
    else:
        comment = get_comment(False, t_pm10_kal_avg, t_pm25_kal_avg, GRAND_TOTALS.year)
        output += comment
    print_output_formatted(output)


def print_summaries(current_day_values: Totals, last: bool) -> None:
    """print_summaries"""
    current_day = current_day_values.current_day
    day_str = GRAND_TOTALS.day.current_day.strftime("%Y-%m-%d")

    if not same_day(current_day, GRAND_TOTALS.day.current_day) or last:
        day_info = GRAND_TOTALS.day.current_day.strftime("%a WK%W")
        print_summary(f"DAG     , {day_str}, {day_info}", GRAND_TOTALS.day)
        if DAY:
            day_of_week_number = GRAND_TOTALS.day.current_day.weekday()
            day_of_week_abbr = GRAND_TOTALS.day.current_day.strftime("%a")
            day_of_week_str = f"{day_of_week_number} {day_of_week_abbr}"
            update_average_totals(f"{day_of_week_str:>8}", GRAND_TOTALS.day)  # 8
        GRAND_TOTALS.day = deepcopy_totals("day", current_day_values)

    if WEEK and (not same_week(current_day, GRAND_TOTALS.week.current_day) or last):
        weeknr = GRAND_TOTALS.week.current_day.strftime("%W")
        week_str = f"WK {weeknr}"
        print_summary(f"WEEK    , {day_str}, {week_str}", GRAND_TOTALS.week)
        _ = D and dbg(f"week_str: {week_str}")
        update_average_totals(f"{week_str:>7}", GRAND_TOTALS.week)  # 7
        GRAND_TOTALS.week = deepcopy_totals("week", current_day_values)

    if MONTH and (not same_month(current_day, GRAND_TOTALS.month.current_day) or last):
        month_info = GRAND_TOTALS.month.current_day.strftime("%b")
        print_summary(
            f"MAAND   , {day_str}, {month_info}",
            GRAND_TOTALS.month,
        )
        month_str = day_str[5:7] + month_info
        _ = D and dbg(f"month_str: {month_str}")
        update_average_totals(f"{month_str:>6}", GRAND_TOTALS.month)  # 6
        GRAND_TOTALS.month = deepcopy_totals("month", current_day_values)

    if not same_year(current_day, GRAND_TOTALS.year.current_day) or last:
        year = GRAND_TOTALS.year.current_day.strftime("%Y")
        number_of_days_pm10 = int(GRAND_TOTALS.year.elapsed_seconds_pm10 / 86400)
        number_of_days_pm25 = int(GRAND_TOTALS.year.elapsed_seconds_pm25 / 86400)
        if YEAR:
            print_summary(
                f"JAAR {number_of_days_pm10:5d}d/{number_of_days_pm25:5d}d, {day_str}, {year}",  # noqa
                GRAND_TOTALS.year,
            )
            _ = D and dbg(f"year {year}")
            update_average_totals(f"{year:>4}", GRAND_TOTALS.year)  # 4
            update_average_totals("alles", GRAND_TOTALS.year)  # 5
            update_average_totals("Alle jaren", GRAND_TOTALS.year)  # 7

        if DAY:
            print_summary(
                f"DAGGEM  , {day_str}, {number_of_days_pm10}d/{number_of_days_pm25}d ",
                GRAND_TOTALS.year,
            )
        if WEEK:
            print_summary(
                f"WEEKGEM , {day_str}, {number_of_days_pm10}d/{number_of_days_pm25}d ",
                GRAND_TOTALS.year,
            )

        if MONTH:
            print_summary(
                f"MAANDGEM, {day_str}, {number_of_days_pm10}d/{number_of_days_pm25}d ",
                GRAND_TOTALS.year,
            )

        if not last:
            GRAND_TOTALS.year = deepcopy_totals("year", current_day_values)


def update_totals(totals: Totals, pm10_kal: float, pm25_kal: float) -> None:
    """update_totals"""
    if pm10_kal >= 0.0:
        totals.elapsed_seconds_pm10 += 3600
        totals.pm10_kal_avg += pm10_kal * 3600
        totals.pm10_kal_min = min(pm10_kal, totals.pm10_kal_min)
        totals.pm10_kal_max = max(pm10_kal, totals.pm10_kal_max)
    if pm25_kal >= 0.0:
        totals.elapsed_seconds_pm25 += 3600
        totals.pm25_kal_avg += pm25_kal * 3600
        totals.pm25_kal_min = min(pm25_kal, totals.pm25_kal_min)
        totals.pm25_kal_max = max(pm25_kal, totals.pm25_kal_max)


def keep_track_of_totals(split: list[str]) -> None:
    """keep_track_of_totals"""
    if D:
        dbg("keep track of totals")
        dbg("     split: " + str(split))
        dbg("    before: " + str(GRAND_TOTALS))

    pm10_kal = get_kal_float(PM10_KAL, split)
    pm25_kal = get_kal_float(PM25_KAL, split)

    update_totals(GRAND_TOTALS.day, pm10_kal, pm25_kal)
    if WEEK:
        update_totals(GRAND_TOTALS.week, pm10_kal, pm25_kal)
    if MONTH:
        update_totals(GRAND_TOTALS.month, pm10_kal, pm25_kal)
    update_totals(GRAND_TOTALS.year, pm10_kal, pm25_kal)

    if D:
        current_day = parser.parse(split[DT])
        print(
            f"{int(GRAND_TOTALS.year.elapsed_seconds_pm10/86400)}/{int(GRAND_TOTALS.year.elapsed_seconds_pm25/86400)} {current_day} year.elapsed_hours: {GRAND_TOTALS.year.elapsed_seconds_pm10}/{GRAND_TOTALS.year.elapsed_seconds_pm25}"  # noqa
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
    split: list[str],
    last: bool,
) -> None:
    """handle_line"""
    _ = D and dbg(f"handle_line: {split}")

    current_day = parser.parse(split[DT])
    if not GRAND_TOTALS.day:
        _ = D and dbg(
            f"not TDAY: {GRAND_TOTALS.day} first time, fill in with initial values"
        )
        values = init(current_day, split)
        GRAND_TOTALS.day = deepcopy_totals("day", values)
        GRAND_TOTALS.week = deepcopy_totals("week", values)
        GRAND_TOTALS.month = deepcopy_totals("month", values)
        GRAND_TOTALS.year = deepcopy_totals("year", values)
        return

    if last or not same_day(current_day, GRAND_TOTALS.day.current_day):
        _ = D and dbg(f"DAY change: {GRAND_TOTALS.day}")
        print_summaries(init(current_day, split), last)
        return

    # take into account totals per line
    if not last:  # skip keep_track_of_totals for last entry
        keep_track_of_totals(split)
        if UUR:
            values = init(current_day, split)
            day_info = current_day.strftime("%Y-%m-%d")
            uur_info = current_day.strftime("%H:%M %a")
            output = f"{STATION_NAME}, UUR, {day_info}, {uur_info}, {values.pm10_kal_avg:.1f}, {values.pm10_kal_min:.0f}, {values.pm10_kal_max:.0f}, {values.who_pm10_daily}, {values.eu_pm10_daily}, {values.pm25_kal_avg:.1f}, {values.pm25_kal_min:.0f}, {values.pm25_kal_max:.0f}, {values.who_pm25_daily},"  # noqa
            output += get_comment(
                False, values.pm10_kal_avg, values.pm25_kal_avg, values
            )
            print_output_formatted(output)
            hour_str = current_day.strftime("%H:%M")
            update_average_totals(f"{hour_str:>10}", values)

    return


def summary() -> None:
    """summary of monitor.csv file"""
    prev_line: str = ""
    GRAND_TOTALS.day = None
    GRAND_TOTALS.week = None
    GRAND_TOTALS.month = None
    GRAND_TOTALS.year = None
    AVERAGE_GRAND_TOTALS["Alle jaren"] = Totals(
        name="Alle jaren",
        current_day=datetime.now(),
        elapsed_seconds_pm10=0,
        elapsed_seconds_pm25=0,
        pm10_kal_avg=0.0,  # avg
        pm10_kal_min=999.9,  # min
        pm10_kal_max=0.0,  # max
        pm25_kal_avg=0.0,  # avg
        pm25_kal_min=999.9,  # min
        pm25_kal_max=0.0,  # max
        who_pm10_daily=0,
        eu_pm10_daily=0,
        who_pm25_daily=0,
    )

    while True:
        line = get_corrected_next_csv_line()
        if line == "":  # EOF
            break  # finish loop
        _ = D and dbg(str(READAHEAD.linecount) + ": LINE=[" + line + "]")
        split = READAHEAD.curr_split
        handle_line(split, False)

        prev_line = line

    # also compute last last day/week/month
    _ = D and dbg("Handling last values")
    # handle end of day for last value
    eod_line = prev_line[0:11] + "23:59" + prev_line[16:]
    last_split = split_on_comma(eod_line)
    _ = D and dbg(f"prev_line: {prev_line}\n eod_line: {eod_line}\n{last_split}")
    if prev_line != "":
        handle_line(last_split, False)
        # and show summaries
        handle_line(last_split, True)


def commas_after(years: list[str], year_index: int, current_year: str, pm_file) -> int:
    """commas after"""
    while year_index < len(years):
        if years[year_index] > current_year:  # write empty years after current year
            pm_file.write(",")
        year_index += 1

    return year_index


def commas_before(years: list[str], year_index: int, year: str, pm_file):
    """commas before"""
    while year_index < len(years) and years[year_index] < year:
        # write empty years before current year
        pm_file.write(",")
        year_index += 1

    return year_index


def write_pm_csv_file(
    pm_avg_file: TextIOWrapper,
    pm_file: TextIOWrapper,
    years: list[str],
    pm_dict: dict[str, str],
):
    """write_pm_csv_file"""
    year_index = 0
    current_station = ""
    current_year = "2000"
    pm_avg_kal_dict: dict[str] = {}
    pm_avg_elapsed_dict: dict[str] = {}

    total_kal = 0.0
    total_elapsed = 0
    for pm_key in sorted(pm_dict):
        (station, year) = pm_key.split(",")
        if current_station != station:
            if current_station != "":
                total_kal_avg = total_kal / total_elapsed
                year_index = commas_after(years, year_index, current_year, pm_file)
                pm_file.write(f",{total_kal_avg:.1f}")
                total_kal = 0.0
                total_elapsed = 0
            pm_file.write(f"\n{station}")
            current_station = station
            year_index = 0
        current_year = year
        year_index = commas_before(years, year_index, year, pm_file)
        entry = pm_dict[pm_key]
        (kal, elapsed_hours) = entry.split(",")
        kal_float = float(kal)
        elapsed_hours_int = int(elapsed_hours)
        total_kal += kal_float
        total_elapsed += elapsed_hours_int

        # keep track of grand totals
        if year in pm_avg_kal_dict:
            pm_avg_kal_dict[year] += kal_float
            pm_avg_elapsed_dict[year] += elapsed_hours_int
        else:
            pm_avg_kal_dict[year] = kal_float
            pm_avg_elapsed_dict[year] = elapsed_hours_int

        kal_avg = kal_float / elapsed_hours_int
        pm_file.write(f",{kal_avg:.1f}")
        year_index += 1

    # write average of last station
    if current_station != "":
        total_kal_avg = total_kal / total_elapsed
        year_index = commas_after(years, year_index, year, pm_file)
        pm_file.write(f",{total_kal_avg:.1f}")

    # write average of grand totals
    year_index = 0
    total_kal = 0.0
    total_elapsed = 0
    for year in sorted(pm_avg_kal_dict.keys()):
        year_index = commas_before(years, year_index, year, pm_avg_file)
        kal_float = pm_avg_kal_dict[year]
        elapsed_hours_int = pm_avg_elapsed_dict[year]
        total_kal += kal_float
        total_elapsed += elapsed_hours_int
        kal_avg = kal_float / elapsed_hours_int
        pm_avg_file.write(f",{kal_avg:.1f}")
        year_index += 1
    total_kal_avg = total_kal / total_elapsed
    year_index = commas_after(years, year_index, year, pm_avg_file)
    pm_avg_file.write(f",{total_kal_avg:.1f}\n")


def write_pm25_pm10_csv_files():
    """write_pm25_pm10_csv_files"""
    header = "Station"
    if YEAR_FILTER:  # make sure all years are written to csv
        for year in range(YEAR_FROM, YEAR_UNTIL + 1):
            if year not in YEARS_DICT:
                YEARS_DICT[f"{year}"] = True

    years = list(YEARS_DICT.keys())
    years.sort()
    for year in years:
        header += ","
        header += year
    header += ",Gemiddeld"

    shrinked_name = STATION_NAME_LIST
    shrinked_name = shrinked_name.replace("_", "")  # get rid of underscores
    shrinked_name = shrinked_name.replace(".txt", "")  # get rid of .txt

    with Path(f"{STATION_NAME_LIST}.pm25.avg.csv").open(
        "w", encoding="utf-8"
    ) as pm25_avg_file:
        with Path(f"{STATION_NAME_LIST}.pm10.avg.csv").open(
            "w", encoding="utf-8"
        ) as pm10_avg_file:
            with Path(f"{STATION_NAME_LIST}.pm25.csv").open(
                "w", encoding="utf-8"
            ) as pm25_file:
                pm25_avg_file.write(f"{header}\n{shrinked_name}")
                pm25_file.write(f"{header}")
                write_pm_csv_file(pm25_avg_file, pm25_file, years, PM25_DICT)

            with Path(f"{STATION_NAME_LIST}.pm10.csv").open(
                "w", encoding="utf-8"
            ) as pm10_file:
                pm10_avg_file.write(f"{header}\n{shrinked_name}")
                pm10_file.write(f"{header}")
                write_pm_csv_file(pm10_avg_file, pm10_file, years, PM10_DICT)


def handle_station_list(station_name_list: str) -> None:
    """handle_station_list"""
    global STATION_NAME, STATION_NAME_KML_PRINTED  # noqa pylint:disable=global-statement
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
                STATION_NAME_KML_PRINTED = False
                input_csv_file = Path(name + ".csv")
                if not input_csv_file.is_file():
                    raise ValueError(f"FOUT: bestand bestaat niet: {input_csv_file}")
                _ = D and dbg(f"Samenvatting genereren uit {input_csv_file}")

                READAHEAD.pm25_kalibration_factor = None
                READAHEAD.pm10_kalibration_factor = None
                READAHEAD.file_eol = False
                READAHEAD.read_done_once = False
                READAHEAD.linecount = 0
                READAHEAD.file = input_csv_file.open("r", encoding="utf-8")

                summary()  # do the work

                if STATION_NAME_KML_PRINTED:  # only write kml if something written
                    all_years = AVERAGE_GRAND_TOTALS["Alle jaren"]
                    number_of_days_pm10 = int(all_years.elapsed_seconds_pm10 / 86400)
                    number_of_days_pm25 = int(all_years.elapsed_seconds_pm25 / 86400)
                    print_summary(
                        f"ALLES {number_of_days_pm10:5d}d/{number_of_days_pm25:5d}d,, alles",  # noqa
                        all_years,
                    )
                    del AVERAGE_GRAND_TOTALS["Alle jaren"]
                    kml_writeln("</description>")
                    kml_write_name(all_years, name)
                    kml_writeln("</Placemark>")
                    print_header()
                READAHEAD.file.close()
                STATION_NAME_KML_PRINTED = True
                print()

    keys = list(AVERAGE_GRAND_TOTALS.keys())
    keys.sort()
    sorted_yearly = {i: AVERAGE_GRAND_TOTALS[i] for i in keys}
    # just put the overall somewhere in the middle of the coordinates

    STATION_NAME_KML_PRINTED = True
    klm_write_placemark(
        station_name_list,
        (KML.max_lat + KML.min_lat) / 2,
        (KML.max_lon + KML.min_lon) / 2,
    )
    for key, totals in sorted_yearly.items():
        elapsed_seconds_pm10 = totals.elapsed_seconds_pm10
        elapsed_seconds_pm25 = totals.elapsed_seconds_pm25
        if elapsed_seconds_pm10 <= 0 or elapsed_seconds_pm25 <= 0:
            continue  # no valid data
        pm10_kal_avg = totals.pm10_kal_avg / elapsed_seconds_pm10
        pm25_kal_avg = totals.pm25_kal_avg / elapsed_seconds_pm25
        number_of_days_pm10 = int(totals.elapsed_seconds_pm10 / 86400)
        number_of_days_pm25 = int(totals.elapsed_seconds_pm25 / 86400)
        if len(key) == 4:
            period = "JAAR"
        elif len(key) == 5:
            period = "ALLES"
        elif len(key) == 6:
            period = "MAAND"
            key = key[3:]
        elif len(key) == 7:
            period = "WEEK"
        elif len(key) == 8:
            period = "DAG"
            key = key[6:]
        elif len(key) == 10:
            period = "UUR"
        else:
            period = "???"
        key = key.strip()
        period = f"{period} {number_of_days_pm10:5d}d/{number_of_days_pm25:5d}d"
        output = f"Gemiddelde,{period},,{key},{pm10_kal_avg:.1f}, {totals.pm10_kal_min:.0f}, {totals.pm10_kal_max:.0f}, {totals.who_pm10_daily}, {totals.eu_pm10_daily}, {pm25_kal_avg:.1f}, {totals.pm25_kal_min:.0f}, {totals.pm25_kal_max:.0f}, {totals.who_pm25_daily},"  # noqa
        comment = get_comment(True, pm10_kal_avg, pm25_kal_avg, totals)
        output += comment
        print_output_formatted(output)
        if len(key) == 4:
            kml_writeln(
                f'{totals.current_day.strftime("%Y"):4s}    {pm10_kal_avg:.1f}/{pm25_kal_avg:.1f} ({number_of_days_pm10}d/{number_of_days_pm25}d) #{totals.who_pm10_daily}/{totals.who_pm25_daily}'  # noqa
            )
            if comment != "":
                comment = comment.replace("; ", "\n     ")
                kml_writeln(f"{comment}\n")

    print_header()
    kml_writeln("</description>")
    last_year = AVERAGE_GRAND_TOTALS[keys[-1]]
    kml_write_name(last_year, station_name_list, True)
    kml_writeln("</Placemark>")


with Path(f"{STATION_NAME_LIST}.kml").open("w", encoding="utf-8") as KML.output_file:
    now_str = datetime_to_datetime_str(datetime.now())
    kml_writeln(
        """<?xml version="1.0" encoding="UTF-8"?>
<kml xmlns="http://www.opengis.net/kml/2.2">
<Document>
<Style id="homeOkStyle"><IconStyle><Icon>
    <href>https://maps.google.com/mapfiles/kml/shapes/ranger_station.png</href></Icon></IconStyle></Style>
<Style id="homeTooHighStyle"><IconStyle><Icon>
    <href>https://maps.google.com/mapfiles/kml/shapes/schools.png</href></Icon></IconStyle></Style>
<Style id="tooHighStyle"><IconStyle><Icon>
    <href>https://maps.google.com/mapfiles/kml/shapes/firedept.png</href></Icon></IconStyle></Style>
<Style id="cautionStyle"><IconStyle><Icon>
    <href>http://maps.google.com/mapfiles/kml/shapes/caution.png</href></Icon></IconStyle></Style>
<Style id="okStyle"><IconStyle><Icon>
    <href>https://maps.google.com/mapfiles/kml/shapes/parks.png</href></Icon></IconStyle></Style>
    """
    )
    kml_writeln(f"<name>{STATION_NAME_LIST} {now_str}</name>")

    handle_station_list(STATION_NAME_LIST)

    kml_writeln("</Document>")
    kml_writeln("</kml>")

write_pm25_pm10_csv_files()
