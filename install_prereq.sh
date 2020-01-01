#!/bin/bash

set -e

sudo apt-get update
sudo apt-get install -y git iw dnsmasq hostapd screen curl build-essential python3-pip python3-setuptools python3-wheel python3-dev mosquitto haveged net-tools libssl-dev

PY_DEPENDENCIES="paho-mqtt pyaes tornado git+https://github.com/M4dmartig4n/sslpsk.git pycrypto"

if python3 -c 'import sys; exit(0) if sys.version_info.major == 3 and sys.version_info.minor < 7 else exit(1)' ;
then
	sudo -H pip3 install $PY_DEPENDENCIES
else
	sudo -H python3 -m pip install $PY_DEPENDENCIES
fi

echo "Ready to start upgrade"
