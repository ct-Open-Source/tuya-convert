#!/bin/bash

set -e

sudo apt-get update
sudo apt-get install -y git iw dnsmasq hostapd screen curl build-essential python3-pip python3-setuptools python3-wheel python3-dev mosquitto haveged net-tools libssl-dev

latest_espurna_version=$(curl -s 'https://api.github.com/repos/xoseperez/espurna/releases/latest' | grep -oP '"tag_name": "\K(.*)(?=")')
curl -Lo files/espurna.bin https://github.com/xoseperez/espurna/releases/download/"$latest_espurna_version"/espurna-"$latest_espurna_version"-espurna-base-1MB.bin

sudo -H python3 -m pip install --upgrade paho-mqtt tornado git+https://github.com/drbild/sslpsk.git pycryptodomex

echo "Ready to start upgrade"
