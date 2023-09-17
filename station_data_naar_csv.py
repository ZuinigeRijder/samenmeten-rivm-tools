# == station_data_naar_csv.py Author: Zuinige Rijder ==========================
"""
Simpel Python3 script to voor ophalen station metingen en schrijf dit naar csv bestand.
"""
from io import TextIOWrapper
import json
from os import path
import logging
import logging.config
from pathlib import Path
import re
import sys

from utils import (
    arg_has,
    datetime_to_datetime_str,
    dbg,
    execute_request,
    get,
    get_last_date_entry,
    iso8601_to_datetime,
    utc_to_local,
)


D = arg_has("debug")

SCRIPT_DIRNAME = path.abspath(path.dirname(__file__))
logging.config.fileConfig(f"{SCRIPT_DIRNAME}/logging_config.ini")
if D:
    logging.getLogger().setLevel(logging.DEBUG)


if len(sys.argv) < 2:
    print(
        """
Gebruik  : python station_data_naar_csv.py bestand_met_station_namen.txt [debug]
Voorbeeld: python station_data_naar_csv.py _heusden.txt
INVOER   : bestand_met_station_namen.txt
UITVOER  : voor iedere station in bestand_met_station_namen.txt schrijf .csv bestand

Opmerking: station namen van een gemeente kun je opvragen met:
           python gemeente_station_namen.py gemeente_code
        """
    )
    sys.exit(-1)


def get_observations_values(url: str, till: str) -> dict:
    """get_observations_values"""
    result_dict = {}
    finished = False
    while not finished:
        print(f"@iot.nextLink={url}")
        content = execute_request(url)
        observations_values = json.loads(content)
        for measurement in get(observations_values, "value"):
            _ = D and dbg(f"measurement:{measurement}")
            result = measurement["result"]
            time = measurement["phenomenonTime"]
            if time <= till:  # got already this result
                finished = True
            else:
                result_dict[time] = result

        url = get(observations_values, "@iot.nextLink")
        if url is None or url == "":
            return result_dict

    return result_dict


def get_observations_data(streams_data: dict, till: str, file: TextIOWrapper) -> None:
    """get_observations_data"""
    match = ["pm10", "pm10_kal", "pm25", "pm25_kal", "rh", "temp"]
    result_dict = {}
    for item in streams_data:
        _ = D and dbg(f"item={item}")
        name = get(item, "name", "naam bestaat niet")
        split = name.split("-")
        data_type = split[len(split) - 1]  # last entry contains data type
        if data_type in match:
            url = get(item, "Observations@iot.navigationLink", "navigationLink absent")
            print(f"\nOphalen data voor type: {data_type}")
            result_list = get_observations_values(url, till)
            result_dict[data_type] = result_list

    pm10_kal = get(result_dict, "pm10_kal", "geen pm10 gecalibreerde data")
    pm10 = get(result_dict, "pm10", "geen pm10 data")
    pm25_kal = get(result_dict, "pm25_kal", "geen pm2.5 gecalibreerde data")
    pm25 = get(result_dict, "pm25", "geen pm2.5 data")
    luchtvochtigheid = get(result_dict, "rh")  # might be absent
    temp = get(result_dict, "temp")  # might be absent

    print()
    pm10_kal_count = len(pm10_kal)
    if pm10_kal_count == 0:
        print(f"Geen nieuwe pm10 calibratie data gevonden sinds {till}")
        return

    print(f"Toevoegen {pm10_kal_count} resultaten aan csv bestand")

    pm10_kal_keys = list(pm10_kal.keys())
    pm10_kal_keys.sort()
    sorted_pm10_kal = {i: pm10_kal[i] for i in pm10_kal_keys}
    for key, value in sorted_pm10_kal.items():
        datetime_str_local = datetime_to_datetime_str(
            utc_to_local(iso8601_to_datetime(key))
        )
        data_to_write = f"{datetime_str_local},{value},{get(pm10, key)},{get(pm25_kal, key)},{get(pm25, key)},{get(luchtvochtigheid, key)},{get(temp, key)}\n"  # noqa
        data_to_write = data_to_write.replace("None", "")  # None values handle as empty
        if D:
            print(data_to_write, end="")
        file.write(data_to_write)


def get_station_data(input_station_name: str) -> None:
    """get_station_data"""
    url = f"https://api-samenmeten.rivm.nl/v1.0/Things?$filter=name%20eq%20%27{input_station_name}%27"  # noqa
    content = execute_request(url)
    station_data = json.loads(content)
    station_data_array = get(station_data, "value", "Geen station data")
    if len(station_data_array) == 0:
        raise ValueError("Lege station data")
    data_streams = station_data_array[0]["Datastreams@iot.navigationLink"]
    content = execute_request(data_streams)
    streams_data = json.loads(content)
    streams_data_value = get(streams_data, "value", "Geen streams data")

    output_station_csv_file = Path(input_station_name + ".csv")
    if not output_station_csv_file.is_file():
        output_station_csv_file.touch()
        print(f"Schrijven van koptekst naar nieuwe csv file {output_station_csv_file}")
        with output_station_csv_file.open("a", encoding="utf-8") as file:
            file.write("datetime,pm10 kal,pm10,pm2.5 kal,pm2.5,rh%,temp\n")

    till = get_last_date_entry(output_station_csv_file, "2000-01-01 00:00")
    print(f"Uitvoer csv bestand: {output_station_csv_file}")
    with output_station_csv_file.open("a", encoding="utf-8") as file:
        get_observations_data(streams_data_value, till, file)


def handle_station_list(station_name_list: str) -> None:
    """handle_station_list"""
    input_file = Path(station_name_list)
    if not input_file.is_file():
        raise ValueError(f"{station_name_list} bestand bestaat niet")
    with input_file.open("r", encoding="utf-8") as file:
        for name in file:
            name = re.sub("#.*", "", name)
            name = name.strip()
            if name != "":
                print(f"Ophalen station data voor {name}")
                get_station_data(name)  # do the work


handle_station_list(sys.argv[1].strip())
