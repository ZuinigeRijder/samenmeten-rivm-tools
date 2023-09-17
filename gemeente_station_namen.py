# === gemeente_station_namen.py Author: Zuinige Rijder ========================
"""
Simpel Python3 script voor ophalen station namen behorende bij gemeente en
schrijft deze naar standaard uitvoer.
"""
import json
from os import path
import logging
import logging.config
import sys

from utils import (
    arg_has,
    execute_request,
    get,
)


D = arg_has("debug")

SCRIPT_DIRNAME = path.abspath(path.dirname(__file__))
logging.config.fileConfig(f"{SCRIPT_DIRNAME}/logging_config.ini")
if D:
    logging.getLogger().setLevel(logging.DEBUG)


if len(sys.argv) < 2:
    print(
        """
Gebruik  : python gemeente_station_namen.py gemeente_code [debug]
Voorbeeld: python gemeente_station_namen.py 797
PARAMETER: gemeente_code
           b.v. gemeente heusden is code 797
           Zie GemeentenAlfabetisch2022.csv voor de codes voor iedere gemeente.
UITVOER  : namen van stations
    """
    )
    sys.exit(-1)


def get_gemeente_station_names(gemeente_code: str) -> None:
    """get_gemeente_station_names"""
    url = f"https://api-samenmeten.rivm.nl/v1.0/Things?$filter=properties/codegemeente%20eq%20%27{gemeente_code}%27"  # noqa
    content = execute_request(url)
    station_data = json.loads(content)
    station_data_array = get(station_data, "value", "Geen stations")
    if len(station_data_array) == 0:
        raise ValueError("Geen station data gevonden")
    for item in station_data_array:
        name = get(item, "name", "Station naam bestaat niet")
        print(name.strip())


get_gemeente_station_names(sys.argv[1].strip())  # do the work
