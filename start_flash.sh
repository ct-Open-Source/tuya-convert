#!/bin/bash
bold=$(tput bold)
normal=$(tput sgr0)
. ./config.txt

./stop_flash.sh >/dev/null

pushd scripts

echo "======================================================"
echo "${bold}TUYA-CONVERT${normal}"
echo
echo "https://github.com/vtrust-de/smarthome-smarthack"
echo "TUYA-CONVERT was developed by Michael Steigerwald from the IT security company VTRUST (https://www.vtrust.de/) in collaboration with the techjournalists Merlin Schumacher, Pina Merkert, Andrijan Moecker and Jan Mahn at c't Magazine. (https://www.ct.de/)"
echo 
echo 
echo "======================================================"
echo "${bold}PLEASE READ THIS CAREFULLY!${normal}"
echo "======================================================"
echo "TUYA-CONVERT creates a fake update server environment for ESP8266/85 based tuya devices. It enables you to backup your devices firmware and upload an alternative one (e.g. ESPEasy, Tasmota, Espurna) without the need to open the device and solder a serial connection (OTA, Over-the-air)."
echo "Please make sure that you understand the consequences of flashing an alternative firmware, since you might lose functionality!"
echo
echo "Flashing an alternative firmware can cause unexpected device behavior and/or render the device unusable. Be aware that you do use this software at YOUR OWN RISK! Please acknowledge that VTRUST and c't Magazine (or Heise Medien GmbH & Co. KG) CAN NOT be held accountable for ANY DAMAGE or LOSS OF FUNCTIONALITY by typing ${bold}yes + Enter${normal}"
echo 
read
if [ "$REPLY" != "yes" ]; then
   exit
fi
echo "======================================================"
echo "  Starting AP in a screen"
sudo screen -L smarthack-wifi.log -S smarthack-wifi -m -d ./setup_ap.sh
echo "  Stopping any Webserver"
sudo service apache2 stop >/dev/null 2>&1
echo "  Starting Websever in a screen"
sudo screen -L smarthack-web.log -S smarthack-web -m -d ./fake-registration-server.py
echo "  Starting Mosquitto in a screen"
sudo service mosquitto stop >/dev/null 2>&1
sudo screen -L smarthack-mqtt.log -S smarthack-mqtt -m -d mosquitto -v
echo
echo "======================================================"
echo
echo "IMPORTANT"
echo "1. Connect any another device (a smartphone or something) to the WIFI $AP"
echo "   The wpa-password is ${bold}$PASS${normal}"
echo "   This step is IMPORTANT otherwise the smartconfig will not work!"
echo "2. Put your IoT device in autoconfig/smartconfig/paring mode (LED will blink fast). This is usually done by pressing and holding the primary button of the device"
echo "3. Press ${bold}ENTER${normal} to continue"
read x
echo ""
echo "======================================================"
echo "Starting pairing procedure in screen"
sudo ip route add 255.255.255.255 dev $WLAN
sudo screen -L smarthack-smartconfig.log -S smarthack-smartconfig -m -d ./smartconfig/smartconfig.js
echo "Waiting for the upgraded device to appear"
echo "If this does not work have a look at the '*.log'-files in the 'scripts' subfolder!"

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
echo "Please make sure to note the correct SPI flash mode!"
echo "Installing an alternative firmware with the wrong flash mode will leave the ESP unable to boot!"
echo
echo "Next steps:"
echo "1. To go back to the orginal software"
echo "   # curl http://10.42.42.42/undo"
echo
echo "2. Be sure the conversion software runs in user2"
echo "   # curl http://10.42.42.42/flash2"
echo
echo "3. Flash a third party firmware to the device"
echo "BE SURE THE FIRMWARE FITS THE DEVICE AND USES THE CORRECT FLASH MODE!"
echo "MAXIMUM SIZE IS 512KB"
echo "put or link it to ./files/thirdparty.bin"
echo "A basic build of Sonoff-Tasmota v6.4.1 is already included in this repository."
echo "   # curl http://10.42.42.42/flash3"
echo "Alternatively let the device download and flash a file via HTTP:"
echo "   # curl http://10.42.42.42/flashURL?url=http://10.42.42.1/files/thirdparty.bin"
echo
echo "HAVE FUN!"


