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

import adafruit_sht31d as sht31d
from busio import I2C
from board import SCL, SDA

SHT31_ADDRESSES = [0x44, 0x45]
AM2302 = "AM2302"
SHT31 = "SHT31"
W1 = "W1"

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
    if humidity is None and temperature is None:
        return (None, None)
    return (round(temperature, 1), round(humidity,1))

def read_sht31(address=0x44):
    """
        Read temperature and humidity data from a SHT31 sensor
        :param int address: 0x44 or 0x45 defaults to 0x44
    """
    if address not in SHT31_ADDRESSES:
        raise ValueError(
            "Invalid address {address} must be one of {addresses}".format(
                address=address,
                addresses=SHT31_ADDRESSES))
    i2c = I2C(SCL, SDA)
    sensor = sht31d.SHT31D(i2c, address=address)
    return (round(sensor.temperature, 1), round(sensor.relative_humidity, 1))


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
                if sensor_type == AM2302:
                    if pin is None:
                        raise ValueError("No pin specified")
                    else:
                        temperature, humidity = read_am2302(pin)
                elif sensor_type == W1:
                    temperature = read_w1()
                elif sensor_type == SHT31:
                    temperature, humidity = read_sht31()
                else:
                    raise ValueError("Unknown sensor type")
                if temperature is not None:
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
    SENSOR_OPTION.add_argument(
        "-s",
        "--sht",
        action="store_true",
        help="Read an SHT-31 sensor")
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
        SENSOR = AM2302
    elif ARGS.w1:
        SENSOR = W1
    elif ARGS.sht:
        SENSOR = SHT31
    else:
        print("Unknown sensor type")
        exit(2)
    if ARGS.pin is None:
        PIN = None
    else:
        PIN = ARGS.pin
    loop(ARGS.name, ARGS.config, SENSOR, ARGS.interval, PIN)
