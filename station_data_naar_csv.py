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
Voorbeeld: python station_data_naar_csv.py _GemeenteHeusden.txt
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
        if D or "skip" in url:
            print(f"\t\t\t@iot.nextLink={url}")
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


def get_keylist(dictionary: dict) -> list:
    """get_keylist"""
    if dictionary is not None:
        return list(dictionary.keys())
    return []


def get_observations_data(
    streams_data: dict,
    till: str,
    file: TextIOWrapper,
    last_pm_10_kal_factor: float,
    last_pm_25_kal_factor: float,
) -> None:
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
            print(f"Ophalen data voor type: {data_type} {url}")
            result_list = get_observations_values(url, till)
            result_dict[data_type] = result_list

    pm10_kal = get(result_dict, "pm10_kal", "geen pm10 gecalibreerde data")
    pm10 = get(result_dict, "pm10", "geen pm10 data")
    pm25_kal = get(result_dict, "pm25_kal", "geen pm2.5 gecalibreerde data")
    pm25 = get(result_dict, "pm25", "geen pm2.5 data")
    luchtvochtigheid = get(result_dict, "rh")  # might be absent
    temp = get(result_dict, "temp")  # might be absent

    # we want to get the union of timestamps of all new data
    key_list = list(
        set().union(
            get_keylist(pm10_kal),
            get_keylist(pm10),
            get_keylist(pm25_kal),
            get_keylist(pm25),
            get_keylist(luchtvochtigheid),
            get_keylist(temp),
        )
    )
    key_list.sort()

    key_count = len(key_list)
    if key_count == 0:
        print(f"Geen nieuwe data gevonden sinds {till}\n")
        return

    print(f"Toevoegen {key_count} resultaten aan csv bestand\n")

    for key in key_list:
        datetime_str_local = datetime_to_datetime_str(
            utc_to_local(iso8601_to_datetime(key))
        )
        pm10_kal_value = get(pm10_kal, key)
        pm10_value = get(pm10, key)
        pm_10_kal_factor = last_pm_10_kal_factor
        if (
            pm10_kal_value is not None
            and pm10_kal_value > 0.0
            and pm10_value is not None
            and pm10_value > 0.0
        ):
            pm_10_kal_factor = pm10_kal_value / pm10_value

        pm25_kal_value = get(pm25_kal, key)
        pm25_value = get(pm25, key)
        pm_25_kal_factor = last_pm_25_kal_factor
        if (
            pm25_kal_value is not None
            and pm25_kal_value > 0.0
            and pm25_value is not None
            and pm25_value > 0.0
        ):
            pm_25_kal_factor = pm25_kal_value / pm25_value

        data_to_write = f"{datetime_str_local},{pm10_kal_value},{pm10_value},{pm25_kal_value},{pm25_value},{get(luchtvochtigheid, key)},{get(temp, key)},{pm_10_kal_factor:.3f},{pm_25_kal_factor:.3f}\n"  # noqa
        data_to_write = data_to_write.replace("None", "")  # None values handle as empty
        if D:
            print(data_to_write, end="")
        file.write(data_to_write)

        last_pm_10_kal_factor = pm_10_kal_factor
        last_pm_25_kal_factor = pm_25_kal_factor


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
            file.write(
                "datetime,pm10 kal,pm10,pm2.5 kal,pm2.5,rh%,temp,pm10 kal factor,pm2.5 kal factor\n"  # noqa
            )

    (till, last_pm_10_kal_factor, last_pm_25_kal_factor) = get_last_date_entry(
        output_station_csv_file, "2000-01-01 00:00"
    )
    print(f"Uitvoer csv bestand: {output_station_csv_file}")
    with output_station_csv_file.open("a", encoding="utf-8") as file:
        get_observations_data(
            streams_data_value, till, file, last_pm_10_kal_factor, last_pm_25_kal_factor
        )


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
