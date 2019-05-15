#!/bin/bash

set -e

sudo apt-get update
sudo apt-get upgrade -y
sudo apt-get install -y dnsmasq hostapd screen curl python3-pip python3-setuptools python3-wheel mosquitto haveged net-tools

PYVERSION=$(python3 -c 'import sys; print(".".join(map(str, sys.version_info[:3])))'|cut -f 1,2 -d \.)
    if (( $(echo "$PYVERSION < 3.7" | bc -l) )); then
      sudo pip3 install paho-mqtt pyaes tornado
    else
      sudo python3 -m pip install paho-mqtt pyaes tornado
    fi
echo "Ready to start upgrade"
