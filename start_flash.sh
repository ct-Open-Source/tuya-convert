#!/bin/bash

. ./config.txt

./stop_flash.sh >/dev/null

pushd scripts

echo "======================================================"
echo "SMARTHOME-SMARTHACK"
echo "https://github.com/vtrust-de/smarthome-smarthack"
echo "USE AT YOUR OWN RISK!!!"
echo "======================================================"
echo "  Starting AP in a screen"
sudo screen -S smarthack-wifi -m -d ./setup_ap.sh


echo "  Stopping any Webserver"
sudo service apache2 stop >/dev/null 2>&1

echo "  Starting Websever in a screen"
sudo screen -S smarthack-web -m -d ./fake-registration-server.py

service mosquitto stop >/dev/null 2>&1
echo "  Starting Mosquitto in a screen"
sudo screen -S smarthack-mqtt -m -d mosquitto -v
echo
echo "======================================================"
echo
echo
echo "USE AT YOUR OWN RISK!!!"
echo "IMPORTANT"
echo "1. Connect any another device (a smartphone or something) to the WIFI $AP"
echo "   The wpa-password is $PASS"
echo "   This step is IMPORTANT otherwise the smartconfig will not work!"
echo "2. Put your IoT device in autoconfig/smartconfig/paring mode (LED will blink fast)"
echo "3. Press ENTER to continue"
read x
echo
echo
echo "======================================================"
echo "Starting pairing procedure in screen"
sudo ip route add 255.255.255.255 dev $WLAN
sudo screen -S smarthack-smartconfig -m -d ./smartconfig/smartconfig.js


echo "Waiting for the upgraded device to appear"

while ! timeout 0.2 ping -c 1 -n 10.42.42.42 &> /dev/null
do
    printf "."
	sleep 1
done

echo
echo "IoT-device is online with ip 10.42.42.42"
echo "Fetching firmware backup"
sleep 2
./backup.py

popd

echo "======================================================"
echo "Getting Info from IoT-device"
curl http://10.42.42.42 2> /dev/null | tee device-info.txt
echo 
echo "======================================================"
echo
echo
echo
echo "Next steps:"
echo "1. To go back to the orginal software"
echo "   # curl http://10.42.42.42/undo"
echo
echo "2. Be sure the conversion software runs in user2"
echo "   # curl http://10.42.42.42/flash2"
echo
echo "3. Flash a third party firmware to the device"
echo "BE SURE THE FIRMWARE FITS TO THE DEVICE"
echo "MAXIMUM SIZE IS 512KB"
echo "put or link it to ./files/thirdparty.bin"
echo "   # curl http://10.42.42.42/flash3"
echo
echo
echo "HAVE FUN!"


