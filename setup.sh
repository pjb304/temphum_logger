#!/bin/bash

sudo raspi-config nonint do_memory_split 16
sudo apt install python3-pip python3-setuptools

sudo pip3 install Adafruit_DHT
pip3 install w1thermsensor
