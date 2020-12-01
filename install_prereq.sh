#!/bin/bash

set -e

if [ $(grep -c "Ubuntu 2" /etc/os-release) -eq "1" ]
then
  echo "Ubuntu 20.04 and later use systemd-resolve as its DNS. This script needs dnsmasq"
  echo "but it could not be installed automatically. Please remove systemd-resolve and"
  echo "check this script to manually install the prequisites, or try another Linux."
  exit 1
fi

sudo apt-get update
sudo apt-get install -y git iw dnsmasq hostapd screen curl build-essential python3-pip python3-setuptools python3-wheel python3-dev mosquitto haveged net-tools libssl-dev

sudo -H python3 -m pip install --upgrade paho-mqtt tornado git+https://github.com/drbild/sslpsk.git pycryptodomex

echo "Ready to start upgrade"
