#!/usr/bin/env python3
from time import sleep
from argparse import ArgumentParser
from urllib.request import urlopen
from json import loads

from temphum_database import TempHumDatabase

def get_external_temp_hum():
    """
        Get temperature and huidity from openweathermap
    """
    data = loads(urlopen("http://api.openweathermap.org/data/2.5/weather?q=Southampton&units=metric&APPID=615df34fae24f3b1e0de372fe3f80bfa", timeout=2).read())[u'main']
    temperature = data[u'temp']
    humidity = data[u'humidity']
    return (temperature, humidity)

def loop(config_file, interval):
    """
        Loop indefinitely and download the readings
    """
    while True:
        db = TempHumDatabase(config_file)
        try:
            while True:
                temperature = None
                humidity = None
                (temperature, humidity) = get_external_temp_hum()
                db.store_reading("outside", temperature, humidity)
                sleep(interval)
        except Exception as exp:
            print(exp)
            sleep(120)


if __name__ == "__main__":
    PARSER = ArgumentParser(
        description="Fetch temperaturre (and humidity) data from openweather and submit to database")
    PARSER.add_argument(
        "-c",
        "--config",
        help="Configuration file to use for database access",
        required=True,
        action="store")
    PARSER.add_argument(
        "-i",
        "--interval",
        action="store",
        required=True,
        type=int,
        help="The interval between readings")
    ARGS = PARSER.parse_args()
    loop(ARGS.config, ARGS.interval)
