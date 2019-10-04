#!/bin/bash

set -e

sudo apt-get update
sudo apt-get upgrade -y
sudo apt-get install -y dnsmasq hostapd screen curl python-pip python3-pip python-setuptools python3-setuptools python3-wheel python-dev python3-dev mosquitto haveged net-tools libssl-dev

PY3_DEPENDENCIES="paho-mqtt pyaes tornado git+https://github.com/M4dmartig4n/sslpsk.git pycrypto"
PY2_DEPENDENCIES="git+https://github.com/M4dmartig4n/sslpsk.git pycrypto"

if python3 -c 'import sys; exit(0) if sys.version_info.major == 3 and sys.version_info.minor < 7 else exit(1)' ;
then
	sudo -H pip3 install $PY3_DEPENDENCIES
	sudo -H pip2 install $PY2_DEPENDENCIES
else
	sudo -H python3 -m pip install $PY3_DEPENDENCIES
	sudo -H python2 -m pip install $PY2_DEPENDENCIES
fi

echo "Ready to start upgrade"
