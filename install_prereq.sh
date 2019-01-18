#!/bin/bash

curl -sL https://deb.nodesource.com/setup_11.x | sudo -E bash -

sudo apt-get update
sudo apt-get upgrade -y
sudo apt-get install -y dnsmasq hostapd screen curl python-pip python-setuptools python-wheel mosquitto nodejs

sudo pip install paho-mqtt pyaes tornado

pushd scripts/smartconfig
npm i
popd

echo "Ready to start upgrade"
