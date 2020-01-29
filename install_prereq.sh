#!/bin/bash

set -e

sudo apt-get update
sudo apt-get install -y git iw dnsmasq hostapd screen curl build-essential python3-pip python3-setuptools python3-wheel python3-dev mosquitto haveged net-tools libssl-dev

sudo -H python3 -m pip install --upgrade paho-mqtt tornado git+https://github.com/drbild/sslpsk.git pycryptodomex

echo "Ready to start upgrade"
