#!/bin/bash

echo "Stopping AP in a screen"
sudo pkill hostapd
sudo screen -S smarthack-web          -X stuff '^C'
sudo screen -S smarthack-smartconfig  -X stuff '^C'
sudo screen -S smarthack-mqtt         -X stuff '^C'
