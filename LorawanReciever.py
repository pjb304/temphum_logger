#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Thu Aug 11 11:15:56 2016
@author: sjj
Modified 09/2017
@author pjb
"""
import json
import logging
from argparse import ArgumentParser
import paho.mqtt.client as mqtt
from temphum_database import TempHumDatabase
from mqtt_config import MqttConfig


DEFAULT_CONFIG = "mqtt-config.ini"
DEFAULT_LOG_LEVEL = logging.INFO
LOGGER = None
DB_CONFIG = None
TTN_CONFIG = None
LOCATION = None
# The callback for when the client receives a CONNACK response from the server.
def on_connect(client, userdata, flags, rc):
    LOGGER.info("Connected with result code %s", str(rc))

    # Subscribing in on_connect() means that if we lose the connection and
    # reconnect then subscriptions will be renewed.


    client.subscribe(TTN_CONFIG.topic, TTN_CONFIG.qos)
    LOGGER.info("TOPIC: %s", str(TTN_CONFIG.topic))
    LOGGER.info("QOS: %s", str(TTN_CONFIG.qos))


# The callback for when a PUBLISH message is received from the server.
def on_message(client, userdata, msg):
    data = json.loads(msg.payload.decode("utf-8"))
    device = data["dev_id"]
    payload = data['payload_fields']
    humidity = float(payload['relative_humidity_3'])
    temperature = float(payload['temperature_2'])
    LOGGER.debug("Temperature = %f Humidity = %f", temperature, humidity)
    try:
        db = TempHumDatabase(DB_CONFIG)
        db.store_reading(LOCATION, temperature, humidity)
    except Exception as e:
        LOGGER.error(e)

def on_subscribe(client, userdata, mid, granted_qos):
    LOGGER.debug("Subscribe %s", mid)


def on_log(client, userdata, level, buf):
    LOGGER.debug("%s %s", str(level), str(buf))


def setup(ttn_config_file, db_config_file, location, log_level=DEFAULT_LOG_LEVEL):
    global LOGGER
    LOGGER = logging.getLogger("MQTT Client")
    LOGGER.setLevel(log_level)
    logging.basicConfig(format='%(asctime)s - %(name)s - %(lineno)d - %(levelname)s - %(message)s')
    global TTN_CONFIG
    TTN_CONFIG = MqttConfig(ttn_config_file)

    TTN_CLIENT = mqtt.Client()
    TTN_CLIENT.on_connect = on_connect
    TTN_CLIENT.on_message = on_message
    TTN_CLIENT.on_subscribe_subscribe = on_subscribe
    TTN_CLIENT.on_log = on_log
    LOGGER.debug("MQTT client created")
    TTN_CLIENT.username_pw_set(TTN_CONFIG.user, TTN_CONFIG.password)
    TTN_CLIENT.connect(TTN_CONFIG.server, TTN_CONFIG.port, TTN_CONFIG.keepalive)
    LOGGER.info("MQTT Server: %s", TTN_CONFIG.server)
    LOGGER.info("MQTT Port: %s", str(TTN_CONFIG.port))
    LOGGER.info("MQTT Keepalive: %s", str(TTN_CONFIG.keepalive))
    LOGGER.info("MQTT Username: %s", str(TTN_CONFIG.user))
    LOGGER.info("MQTT Password: %s", str(TTN_CONFIG.password))
    global  DB_CONFIG
    LOGGER.info("DB config: %s", db_config_file)
    DB_CONFIG = db_config_file
    global LOCATION
    LOCATION = location
    LOGGER.info("Location: %s", location)
    try:
        TTN_CLIENT.loop_forever()
    except KeyboardInterrupt:
        TTN_CLIENT.loop_stop()

if __name__ == "__main__":
    global OUTPUT_FILE
    PARSER = ArgumentParser(
        description="Get the data from a ttn-node")
    LOGGING_OUTPUT = PARSER.add_mutually_exclusive_group()
    LOGGING_OUTPUT.add_argument(
        "-q",
        "--quiet",
        action="store_true",
        help="Suppress most ouput")
    LOGGING_OUTPUT.add_argument(
        "-v",
        "--verbose",
        action="store_true",
        help="Maximum verbosity output on command line")
    PARSER.add_argument(
        "-t", "--ttn-config", action="store",
        dest="ttn_config_file",
        help="TTN Configuration file",
        required=True)
    PARSER.add_argument(
        "-d", "--db-config", action="store",
        dest="db_config_file",
        help="DB Configuration file",
        required=True)
    PARSER.add_argument(
        "-l", "--location",
        action="store",
        required=True,
        help="Location name for use in database")
    ARGS = PARSER.parse_args()
    LOG_LEVEL = logging.WARN
    if ARGS.quiet:
        LOG_LEVEL = logging.ERROR
    elif ARGS.verbose:
        LOG_LEVEL = logging.DEBUG
#    try:
    setup(ARGS.ttn_config_file, ARGS.db_config_file, ARGS.location, LOG_LEVEL)
#    except Exception as EX:
#        print(str(EX))
#        exit(1)
