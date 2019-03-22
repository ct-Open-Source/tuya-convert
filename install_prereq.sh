#!/bin/bash

set -e

which curl &> /dev/null || {
    sudo apt-get update
    sudo apt-get install -y curl
}

which node &> /dev/null || {
    curl -sL https://deb.nodesource.com/setup_11.x | sudo -E bash -
}

sudo apt-get update
sudo apt-get upgrade -y
sudo apt-get install -y dnsmasq hostapd screen curl python3-pip python3-setuptools python3-wheel mosquitto nodejs haveged

sudo pip3 install paho-mqtt pyaes tornado

which npm &> /dev/null || {
    echo "cannot find npm. please install nodejs manually."
    exit 1
}
pushd scripts/smartconfig
npm i
popd

echo "Ready to start upgrade"
