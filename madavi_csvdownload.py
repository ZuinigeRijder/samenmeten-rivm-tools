# == madavi_csvdownload.py Author: Zuinige Rijder ==========================
"""
Simple Python3 script to download madavi csv files from https://api-rrd.madavi.de
"""
import sys
from os import path
import logging
import logging.config
from urllib.request import urlretrieve
from zipfile import ZipFile
from utils import arg_has, dbg, execute_request

D = arg_has("debug")

SCRIPT_DIRNAME = path.abspath(path.dirname(__file__))
logging.config.fileConfig(f"{SCRIPT_DIRNAME}/logging_config.ini")
if D:
    logging.getLogger().setLevel(logging.DEBUG)


if len(sys.argv) < 2:
    print(
        """
Usage    : python csvdownload.py chip-id [debug]
Example  : python csvdownload.py esp8266-10147413

Notes:
- the script will download zip and csv files to the current directory
- if the zip file already exists, it will not be downloaded again
- the downloaded zip file is extracted to the current directory
- csv files of the current month are redownloaded,
  because new data might be added since previous download
- chip-id is the combination of sensor type (e.g. SDS011 is esp8266)
  and ID (e.g. 10147413) of the sensor
- ID of the sensor can be found in the local access to your sensor,
  e.g. 1342840 in this screenshot:
  https://github.com/opendata-stuttgart/sensors-software/issues/633#issuecomment-574354727
        """
    )
    sys.exit(-1)

MADAVI_URL = "https://api-rrd.madavi.de/"
MATCH_START = "Datei: <a href='"
CHIP_ID = sys.argv[1]


def unzip(zipfile: str):
    """unzip"""
    print(f"Unzipping  : {zipfile}\n")
    with ZipFile(zipfile, "r") as zip_object:
        zip_object.extractall(path=".")  # extract in current directory


def download(url: str):
    """download"""
    basename = url.split("/")[-1]
    _ = D and dbg(f"basename=[{basename}]")
    if ".csv" in basename or not path.isfile(basename):  # zip not already downloaded
        print(f"Downloading: {basename}")
        filename, headers = urlretrieve(url, basename)
        if D:
            print(f"filename={filename}")
            for name, value in headers.items():
                print(name, value)
        if ".zip" in basename:
            unzip(basename)


def get_links():
    """get_links"""
    url = f"{MADAVI_URL}csvfiles.php?sensor={CHIP_ID}"  # noqa
    content = execute_request(url)
    _ = D and dbg(f"content={content}")
    for line in content.splitlines():
        i_match_start = line.find(MATCH_START)
        if i_match_start > 0:
            _ = D and dbg(f"line:[{line}]")
            i_match_start = i_match_start + len(MATCH_START)
            part = line[i_match_start:]
            _ = D and dbg(f"match start:[{part}]")
            i_match_end = part.find("'>")
            if i_match_end > 0:
                part = part[:i_match_end]
                _ = D and dbg(f"match whole:[{part}]")
                download_url = f"{MADAVI_URL}{part}"
                download(download_url)


get_links()
