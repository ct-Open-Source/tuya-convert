#!/bin/bash

sudo screen -S smarthack-web          -X stuff '^C'
sudo screen -S smarthack-smartconfig  -X stuff '^C'
sudo screen -S smarthack-mqtt         -X stuff '^C'
sudo screen -S smarthack-psk          -X stuff '^C'
echo "Closing AP"
sudo pkill hostapd
