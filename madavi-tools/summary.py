# == summary.py Author: Zuinige Rijder ==========================
"""
Simple Python3 script to read csv files and producing a summary
"""

from dataclasses import dataclass
from datetime import datetime
import glob
from os import path
import logging
import logging.config
import sys

from utils import arg_has, dbg, to_float, utc_to_local

D = arg_has("debug")

SCRIPT_DIRNAME = path.abspath(path.dirname(__file__))
logging.config.fileConfig(f"{SCRIPT_DIRNAME}/logging_config.ini")
if D:
    logging.getLogger().setLevel(logging.DEBUG)


if len(sys.argv) > 2:
    print(
        """
Usage    : python summary.py [debug]

Notes:
- the script will read all csv files in the current directory in alphabetic order
        """
    )
    sys.exit(-1)


@dataclass
class Daily:
    """daily"""

    prev_date: str = ""
    pm10_count: int = 0
    pm10_min: float = 9999.9
    pm10_max: float = 0.0
    pm10_max_dt: str = ""
    pm10_avg: float = 0.0
    pm25_count: int = 0
    pm25_min: float = 9999.9
    pm25_max: float = 0.0
    pm25_max_dt: str = ""
    pm25_avg: float = 0.0


DAILY: Daily = Daily()


def to_local_datetime(dt_str: str):
    """to_local_datetime"""
    _ = D and dbg(f"to_local_datetime: {dt_str}")
    utc = datetime.strptime(dt_str, "%Y-%m-%d %H:%M:%S")
    _ = D and dbg(f"utc: {utc}")
    dt = utc_to_local(utc)
    return dt


def to_local_time_str(dt: datetime):
    """to_local_time_str"""
    _ = D and dbg(f"to_local_time_str: {dt}")
    return datetime.strftime(dt, "%Y-%m-%d %H:%M:%S")


def print_daily_stats():
    """print_daily_stats"""
    DAILY.pm10_avg = DAILY.pm10_avg / DAILY.pm10_count
    DAILY.pm25_avg = DAILY.pm25_avg / DAILY.pm25_count
    pm10_max_dt = to_local_time_str(DAILY.pm10_max_dt)
    pm25_max_dt = to_local_time_str(DAILY.pm25_max_dt)
    print(
        f"{DAILY.prev_date},{DAILY.pm10_max:.2f},{pm10_max_dt},{DAILY.pm10_avg:.2f},{DAILY.pm10_min:.2f},{DAILY.pm25_max:.2f},{pm25_max_dt},{DAILY.pm25_avg:.2f},{DAILY.pm25_min:.2f}"  # noqa
    )


def process_csv_file(csvfile: str):
    """process_csv_file"""
    global DAILY  # noqa pylint: disable=global-statement
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
                    current_date = datetime.strftime(dt, "%Y-%m-%d")
                    init = False
                    if DAILY.prev_date == "":
                        init = True
                    elif DAILY.prev_date != current_date:
                        init = True
                        print_daily_stats()
                    if init:
                        DAILY = Daily()
                        DAILY.prev_date = current_date
                    pm10 = to_float(splitted[7])
                    DAILY.pm10_count += 1
                    DAILY.pm10_avg += pm10
                    if pm10 > DAILY.pm10_max:
                        DAILY.pm10_max = pm10
                        DAILY.pm10_max_dt = dt
                    if pm10 < DAILY.pm10_min:
                        DAILY.pm10_min = pm10
                    pm25 = to_float(splitted[8])
                    DAILY.pm25_count += 1
                    DAILY.pm25_avg += pm25
                    if pm25 > DAILY.pm25_max:
                        DAILY.pm25_max = pm25
                        DAILY.pm25_max_dt = dt
                    if pm25 < DAILY.pm25_min:
                        DAILY.pm25_min = pm25


def get_csv_files():
    """get_csv_files"""
    filelist = glob.glob("*.csv")
    if len(filelist) > 0:
        print(
            "DateTime, PM10 max, PM10 max datetime, PM10 avg, PM10 min, PM2.5 max, PM2.5 max datetime, PM2.5 avg, PM2.5 min"  # noqa
        )
    for csvfile in sorted(filelist):
        process_csv_file(csvfile)
    if len(filelist) > 0:  # also last day
        print_daily_stats()


get_csv_files()
