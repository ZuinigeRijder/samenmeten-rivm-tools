# == utils.py Author: Zuinige Rijder =========
# pylint:disable=logging-fstring-interpolation
"""
utils
"""


from datetime import datetime
import logging
import os
from pathlib import Path
import socket
import sys
import time
import traceback
from typing import Optional
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen

D = False


def set_debug(debug):
    """set debug"""
    global D  # pylint:disable=global-statement
    D = debug


def dbg(line: str) -> bool:
    """print line if debugging"""
    print(line)
    return True  # just to make a lazy evaluation expression possible


def log(msg: str) -> None:
    """log a message prefixed with a date/time format yyyymmdd hh:mm:ss"""
    logging.info(datetime.now().strftime("%Y%m%d %H:%M:%S") + ": " + msg)


def arg_has(string: str) -> bool:
    """arguments has string"""
    for i in range(1, len(sys.argv)):
        if sys.argv[i].lower() == string:
            return True
    return False


def get(dictionary: dict, key: str, fail_string: Optional[str] = None):
    """get"""
    if dictionary is not None and key in dictionary:
        return dictionary[key]
    if fail_string is None:
        return None
    raise ValueError(f"ophaal FOUT: {fail_string}")


def safe_divide(numerator: float, denumerator: float) -> float:
    """safe_divide"""
    if denumerator == 0.0:
        return 0.0
    return numerator / denumerator


def to_int(string: str) -> int:
    """convert to int"""
    if "None" in string:
        return -1
    return round(to_float(string))


def to_float(string: str) -> float:
    """convert to float"""
    if "None" in string:
        return 0.0
    if string == "":
        return 0.0
    return float(string.strip())


def is_true(string: str) -> bool:
    """return if string is true (True or not 0 digit)"""
    if "None" in string:
        return False
    tmp = string.strip().lower()
    if tmp == "true":
        return True
    elif tmp == "false":
        return False
    else:
        return tmp.isdigit() and tmp != "0"


def same_year(d_1: datetime, d_2: datetime) -> bool:
    """return if same year"""
    return d_1.year == d_2.year


def same_month(d_1: datetime, d_2: datetime) -> bool:
    """return if same month"""
    if d_1.month != d_2.month:
        return False
    return d_1.year == d_2.year


def same_week(d_1: datetime, d_2: datetime) -> bool:
    """return if same week"""
    if d_1.isocalendar().week != d_2.isocalendar().week:
        return False
    return d_1.year == d_2.year


def same_day(d_1: datetime, d_2: datetime) -> bool:
    """return if same day"""
    if d_1.day != d_2.day:
        return False
    if d_1.month != d_2.month:
        return False
    return d_1.year == d_2.year


def split_on_comma(text: str) -> list[str]:
    """split string on comma and strip spaces around strings"""
    result = [x.strip() for x in text.split(",")]
    return result


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


def iso8601_to_datetime(iso8601: str) -> datetime:
    """iso8601_to_datetime"""
    date = datetime.strptime(iso8601, "%Y-%m-%dT%H:%M:%S.%fZ")
    return date


def datetime_to_datetime_str(date: datetime) -> str:
    """datetime_to_datetime_str"""
    datetime_str = datetime.strftime(date, "%Y-%m-%d %H:%M")
    return datetime_str


def datetime_str_to_datetime(yyyy_mm_dd_hh_mm: str) -> datetime:
    """datetime_str_to_datetime"""
    date = datetime.strptime(yyyy_mm_dd_hh_mm, "%Y-%m-%d %H:%M")
    return date


def datetime_to_iso8601_str(date: datetime) -> str:
    """datetime_to_iso8601_str"""
    return datetime.strftime(date, "%Y-%m-%dT%H:%M:%S.%f")[:-3] + "Z"


def utc_to_local(utc: datetime) -> datetime:
    """utc_to_local"""
    epoch = time.mktime(utc.timetuple())
    offset = datetime.fromtimestamp(epoch) - datetime.utcfromtimestamp(epoch)
    return utc + offset


def local_to_utc(local: datetime) -> datetime:
    """local_to_utc"""
    epoch = time.mktime(local.timetuple())
    offset = datetime.fromtimestamp(epoch) - datetime.utcfromtimestamp(epoch)
    return local - offset


def get_last_line(file_path: Path) -> str:
    """get last line of file_path"""
    last_line = ""
    if file_path.is_file():
        with open(file_path.name, "rb") as file:
            try:
                file.seek(-2, os.SEEK_END)
                while file.read(1) != b"\n":
                    file.seek(-2, os.SEEK_CUR)
            except OSError:
                file.seek(0)
            last_line = file.readline().decode().strip()
    return last_line


def get_last_date_entry(csv_file: Path, start_yyyymmddhh: str):
    """get last date entry"""
    last_line = get_last_line(csv_file)
    last_yyyymmddhh = start_yyyymmddhh
    last_pm_10_kal_factor = 1.0
    last_pm_25_kal_factor = 1.0
    if last_line.startswith("20"):  # year starts with 20
        splitted = last_line.split(",")
        last_yyyymmddhh = splitted[0]
        if len(splitted) > 8:
            last_pm_10_kal_factor = float(splitted[7].strip())
            last_pm_25_kal_factor = float(splitted[8].strip())

    # convert local time to utc time iso8601
    iso8601_utc_string = datetime_to_iso8601_str(
        local_to_utc(datetime_str_to_datetime(last_yyyymmddhh))
    )
    print(
        f"Laatste datum locale tijd: {last_yyyymmddhh} -> iso8601 utc: {iso8601_utc_string}"  # noqa
    )
    return iso8601_utc_string, last_pm_10_kal_factor, last_pm_25_kal_factor


def sleep(retries: int) -> int:
    """handle retries"""
    retries -= 1
    if retries >= 0:
        log("1 minuut slapen")
        time.sleep(60)
    else:
        raise ValueError("Te veel nieuwe pogingen")
    return retries


def execute_request(url: str) -> str:
    """execute request and handle errors"""
    retry = 3
    while True:
        retry -= 1
        request = Request(url)
        errorstring = ""
        try:
            with urlopen(request, timeout=30) as response:
                body = response.read()
                content = body.decode("utf-8")
                if logging.DEBUG >= logging.root.level:
                    logging.debug(f"url: {url}\n{content}\n")
                return content
        except HTTPError as error:
            errorstring = str(error.status) + ": " + error.reason
        except URLError as error:
            errorstring = str(error.reason)
        except TimeoutError:
            errorstring = "Verzoek is verlopen"
        except socket.timeout:
            errorstring = "Socket is verlopen"
        except Exception as ex:  # pylint: disable=broad-except
            errorstring = "urlopen exceptie: " + str(ex)
            traceback.print_exc()

        logging.error(url + " -> " + errorstring)
        retry = sleep(retry)  # retry after 1 minute
