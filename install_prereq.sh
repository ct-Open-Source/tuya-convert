#!/bin/bash

curl -sL https://deb.nodesource.com/setup_11.x | sudo -E bash -

sudo apt-get update
sudo apt-get upgrade -y
sudo apt-get install -y dnsmasq hostapd screen curl python3-pip python3-setuptools python3-wheel mosquitto nodejs haveged

sudo pip3 install paho-mqtt pyaes tornado

pushd scripts/smartconfig
npm i
popd

echo "Ready to start upgrade"
