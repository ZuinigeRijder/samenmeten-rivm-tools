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
   python to_samenmeten_rivm_tools_format.py chip-id samenmeten-sensor-name [debug]
Inputfiles:
   chip-id*.csv
   samenmeten-sensor-name.csv
Outputfile:
   samenmeten-sensor-name.madavi.csv
Example:
   python to_samenmeten_rivm_tools_format.py esp8266-10147413 LTD_54311

Notes:
- the script will read all csv files starting with chip-id in the current directory
- samenmeten-sensor-name.csv is used to get the kalibration factors for PM10 and PM2.5
  and convert this to a format compatible with samenmeten-rivm-tools
- datetime,pm10 kal,pm10,pm2.5 kal,pm2.5,rh%,temp,pm10 kal factor,pm2.5 kal factor
- output is in file samenmeten-sensor-name.madavi.csv
        """
    )
    sys.exit(-1)

CHIP_ID = sys.argv[1]
SENSOR_NAME = sys.argv[2]


def process_csv_file(csvfile: str):
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
                    pm10 = to_float(splitted[7])  # column SDS_P1
                    pm25 = to_float(splitted[8])  # column SDS_P2
                    temp = to_float(splitted[15])  # column BME280_temperature
                    rh = to_float(splitted[16])  # column BME280_humidity
                    print(
                        f"{dt},pm10 kal,{pm10},pm2.5 kal,{pm25},{rh},{temp},pm10 kal factor,pm2.5 kal factor"  # noqa
                    )


def get_csv_files():
    """get_csv_files"""
    filelist = glob.glob(f"data-{CHIP_ID}*.csv")
    if len(filelist) > 0:
        print(
            "datetime,pm10 kal,pm10,pm2.5 kal,pm2.5,rh%,temp,pm10 kal factor,pm2.5 kal factor"  # noqa
        )
    for csvfile in sorted(filelist):
        process_csv_file(csvfile)


get_csv_files()
