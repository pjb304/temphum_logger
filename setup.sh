#!/bin/bash

sudo raspi-config nonint do_memory_split 16
sudo raspi-config nonint do_w1 0
sudo apt install python3-pip python3-setuptools

echo "---------- Install package for AM2302 ----------"
cd $HOME
if [ -d "Adafruit_Python_DHT" ]; then
  sudo rm -rf Adafruit_Python_DHT
fi
git clone https://github.com/adafruit/Adafruit_Python_DHT.git
cd Adafruit_Python_DHT
sudo python3 setup.py install

pip install mysqlclient configobj w1thermsensor

