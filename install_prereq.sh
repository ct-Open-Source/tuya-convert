#!/bin/bash

set -e

sudo apt-get update
sudo apt-get upgrade -y
sudo apt-get install -y dnsmasq hostapd screen curl python-pip python3-pip python3-setuptools python3-wheel python3-dev mosquitto haveged net-tools libssl-dev
sudo -H pip3 install paho-mqtt pyaes tornado git+https://github.com/M4dmartig4n/sslpsk.git pycrypto
sudo -H pip2 install git+https://github.com/M4dmartig4n/sslpsk.git pycrypto

echo "Ready to start upgrade"
