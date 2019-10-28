#!/bin/bash

sudo raspi-config nonint do_memory_split 16
sudo raspi-config nonint do_w1 0
sudo apt install python3-pip python3-setuptools  libmariadb-dev

pip3 install mysqlclient configobj w1thermsensor Adafruit_DHT

