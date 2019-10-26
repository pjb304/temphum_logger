#!/usr/bin/env python3
"""
    Philip Basford
    October 2019
"""

import time
from argparse import ArgumentParser
import MySQLdb
import Adafruit_DHT
from w1thermsensor import W1ThermSensor
from temphum_database import TempHumDatabase


def read_w1():
    """
        Read the one-wire sensor to get a temperature reading
    """
    sensor = W1ThermSensor()
    return float(sensor.get_temperature())

def read_am2302(pin):
    """
        Read temperature and humidity data from an AM2302 sensor
    """
    for _ in range(0,5):
        humidity, temperature = Adafruit_DHT.read(Adafruit_DHT.DHT22, pin)
        if humidity is not None and temperature is not None:
            break
        else:
            time.sleep(1)
    return (round(temperature, 1), round(humidity,1))


def loop(device, config_file, sensor_type, interval, pin=None):
    """
        Loop indefintely and take the readings from the specified sensor
    """
    while True:
            db = TempHumDatabase(config_file)
        #try:
            while True:
                temperature = None
                humidity = None
                if sensor_type == "AM2302":
                    if pin is None:
                        raise ValueError("No pin specified")
                    else:
                        temperature, humidity = read_am2302(pin)
                elif sensor_type == "w1":
                    temperature = read_w1()
                else:
                    raise ValueError("Unknown sensor type")
                db.store_reading(device, temperature, humidity)
                time.sleep(interval)
        #except MySQLdb.OperationError as exp:
        #    print(exp)
        #    time.sleep(120)

if __name__ == "__main__":
    PARSER = ArgumentParser(
        description="Read temperature (and humidity) data and submit to database")
    PARSER.add_argument(
        "-c",
        "--config",
        help="Configuration file to use for database access",
        required=True,
        action="store")
    PARSER.add_argument(
        "-n",
        "--name",
        required=True,
        action="store",
        help="Location name")
    SENSOR_OPTION = PARSER.add_mutually_exclusive_group(required=True)
    SENSOR_OPTION.add_argument(
        "-a",
        "--am2302",
        action="store_true",
        help="Read from an AM2302")
    SENSOR_OPTION.add_argument(
        "-w",
        "--w1",
        action="store_true",
        help="Read a 1-wire sensor")
    PARSER.add_argument(
        "-i",
        "--interval",
        action="store",
        required=True,
        type=int,
        help="The interval between readings")
    PARSER.add_argument(
        "-p",
        "--pin",
        action="store",
        type=int,
        help="The pin to use for the sensor")
    ARGS = PARSER.parse_args()
    if ARGS.am2302 and ARGS.pin is None:
        PARSER.error("AM2302 requires a pin to be set")
    SENSOR = ""
    if ARGS.am2302:
        SENSOR = "am2302"
    elif ARGS.w1:
        SENSOR="w1"
    else:
        print("Unknown sensor type")
        exit(2)
    if ARGS.pin is None:
        PIN = None
    else:
        PIN = ARGS.pin
    loop(ARGS.name, ARGS.config, SENSOR, ARGS.interval, PIN)
