#!/bin/bash

sudo apt-get update
sudo apt-get upgrade -y
sudo apt-get install -y dnsmasq hostapd screen curl python3-pip python3-setuptools python3-wheel mosquitto

sudo pip3 install paho-mqtt pyaes tornado

echo "Ready to start upgrade"
