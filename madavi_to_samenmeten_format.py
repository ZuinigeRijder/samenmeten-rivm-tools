# == madavi_to_samenmeten_format.py Author: Zuinige Rijder ================
"""
Simple Python3 script to read madavi csv files and producing a csv
format compatible to samenmeten-rivm-tools (which is bassed on hourly values):
datetime,pm10 kal,pm10,pm2.5 kal,pm2.5,rh%,temp,pm10 kal factor,pm2.5 kal factor

Output will be written to samenmeten-sensor-name.madavi.csv with all measurements.
"""

import glob
from os import path
import logging
import logging.config
from pathlib import Path
import sys

from utils import arg_has, dbg, set_debug, to_float, to_local_datetime

D = arg_has("debug")
set_debug(D)

SCRIPT_DIRNAME = path.abspath(path.dirname(__file__))
logging.config.fileConfig(f"{SCRIPT_DIRNAME}/logging_config.ini")
if D:
    logging.getLogger().setLevel(logging.DEBUG)


arglen = len(sys.argv)
if arglen == 1 or arglen < 3 or arglen > 4:
    print(
        """
Usage:
   python to_samenmeten_rivm_tools_format.py chip-id samenmeten-sensor.csv [debug]
Inputfiles:
   chip-id*.csv
   samenmeten-sensor.csv
Outputfile:
   samenmeten-sensor.madavi.csv
Example:
   python to_samenmeten_rivm_tools_format.py esp8266-10147413 LTD_54311.csv

Notes:
- the script will read all csv files starting with chip-id in the current directory
- samenmeten-sensor.csv is used to get the kalibration factors for PM10 and PM2.5
- write samenmeten-sensor.madavi.csv with format compatible with samenmeten-rivm-tools
  datetime,pm10 kal,pm10,pm2.5 kal,pm2.5,rh%,temp,pm10 kal factor,pm2.5 kal factor
- note that the result contains all madavi data, so not hourly data
- samenvatting.py takes care of non-hourly data
        """
    )
    sys.exit(-1)

CHIP_ID = sys.argv[1]
SENSOR_CSV = sys.argv[2]

PM25_KAL_FACTOR_DICT: dict[str, float] = {}
PM10_KAL_FACTOR_DICT: dict[str, float] = {}


def process_csv_file(csvfile: str, result: list[str]):
    """process_csv_file"""
    _ = D and dbg(f"Processing: {csvfile}")
    with open(csvfile, encoding="utf-8") as f:
        count = 0
        for line in f:
            line = line.strip()
            count += 1
            _ = D and dbg(f"{count}: {line}")
            if len(line) > 0 and line[0].isdigit():
                splitted = line.split(";")
                if len(splitted) > 8:
                    dt = to_local_datetime(splitted[0].replace("/", "-"))
                    timestamp = dt.strftime("%Y-%m-%d %H")
                    pm10_kal_factor = PM10_KAL_FACTOR_DICT.get(timestamp, 1.0)
                    pm25_kal_factor = PM25_KAL_FACTOR_DICT.get(timestamp, 1.0)
                    pm10 = to_float(splitted[7])  # column SDS_P1
                    pm25 = to_float(splitted[8])  # column SDS_P2
                    temp = to_float(splitted[15])  # column BME280_temperature
                    rh = to_float(splitted[16])  # column BME280_humidity
                    pm10_kal = pm10 * pm10_kal_factor
                    pm25_kal = pm25 * pm25_kal_factor
                    result.append(
                        f"{dt},{pm10_kal:.2f},{pm10},{pm25_kal:.2f},{pm25},{rh},{temp},{pm10_kal_factor},{pm25_kal_factor}"  # noqa
                    )


def read_kalibration():
    """read kalibration"""
    with open(SENSOR_CSV, encoding="utf-8") as f:
        count = 0
        for line in f:
            line = line.strip()
            count += 1
            _ = D and dbg(f"{count}: {line}")
            if count > 1:
                splitted = line.split(",")
                if len(splitted) == 9:
                    timestamp = splitted[0][0:13]
                    pm10_kal_factor = to_float(splitted[7])
                    pm25_kal_factor = to_float(splitted[8])
                    if D:
                        print(
                            f"timestamp: {timestamp}, {pm10_kal_factor}, {pm25_kal_factor}"  # noqa
                        )
                    PM10_KAL_FACTOR_DICT[timestamp] = pm10_kal_factor
                    PM25_KAL_FACTOR_DICT[timestamp] = pm25_kal_factor


def get_csv_files():
    """get_csv_files"""
    filelist = glob.glob(f"data-{CHIP_ID}*.csv")
    result: list[str] = []
    for csvfile in sorted(filelist):
        process_csv_file(csvfile, result)

    result.sort()
    outputfile = Path(SENSOR_CSV).stem
    outputfile = f"{outputfile}.madavi.csv"
    print(f"Writing: {outputfile}")
    with open(outputfile, "w", encoding="utf-8") as f:
        f.write(
            "datetime,pm10 kal,pm10,pm2.5 kal,pm2.5,rh%,temp,pm10 kal factor,pm2.5 kal factor\n"  # noqa
        )
        for line in result:
            f.write(f"{line}\n")


read_kalibration()
get_csv_files()
