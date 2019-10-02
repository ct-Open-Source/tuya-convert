#!/bin/bash
bold=$(tput bold)
normal=$(tput sgr0)
screen_minor=`screen --version | cut -d . -f 2`
if [ $screen_minor -gt 5 ]; then
    screen_with_log="sudo screen -L -Logfile"
elif [ $screen_minor -eq 5 ]; then
    screen_with_log="sudo screen -L"
else
    screen_with_log="sudo screen -L -t"
fi
. ./config.txt

./stop_flash.sh >/dev/null

pushd scripts >/dev/null

if [ ! -f eula_accepted ]; then
	echo "======================================================"
	echo "${bold}TUYA-CONVERT${normal}"
	echo
	echo "https://github.com/ct-Open-Source/tuya-convert"
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
	touch eula_accepted
fi
echo "======================================================"
echo -n "  Starting AP in a screen"
$screen_with_log smarthack-wifi.log -S smarthack-wifi -m -d ./setup_ap.sh
while ! ping -c 1 -W 1 -n 10.42.42.1 &> /dev/null; do
	printf .
done
echo "  Stopping any apache web server"
sudo service apache2 stop >/dev/null 2>&1
echo "  Starting web server in a screen"
$screen_with_log smarthack-web.log -S smarthack-web -m -d ./fake-registration-server.py
echo "  Starting Mosquitto in a screen"
sudo service mosquitto stop >/dev/null 2>&1
$screen_with_log smarthack-mqtt.log -S smarthack-mqtt -m -d mosquitto -v
echo
REPLY=y
while [[ $REPLY =~ ^[Yy]$ ]]; do
echo "======================================================"
echo
echo "IMPORTANT"
echo "1. Connect any other device (a smartphone or something) to the WIFI $AP"
echo "   The wpa-password is ${bold}$PASS${normal}"
echo "   This step is IMPORTANT otherwise the smartconfig will not work!"
echo "2. Put your IoT device in autoconfig/smartconfig/pairing mode (LED will blink fast). This is usually done by pressing and holding the primary button of the device"
echo "3. Press ${bold}ENTER${normal} to continue"
read x
echo ""
echo "======================================================"

echo "Starting smart config pairing procedure"
./smartconfig/main.py &
smartconfig_pid=$!

echo "Waiting for the device to install the intermediate firmware"
echo "If this does not work have a look at the '*.log'-files in the 'scripts' subfolder!"

i=60
while ! ping -c 1 -W 1 -n 10.42.42.42 &> /dev/null; do
	printf .
	if (( --i == 0 )); then
		echo
		echo "Device did not appear with the intermediate firmware"
		echo "Stopping smart config"
		kill $smartconfig_pid &>/dev/null
		wait $! 2>/dev/null
		read -p "Do you want to flash another device? [y/N] " -n 1 -r
		echo
		continue 2
	fi
done

echo
echo "IoT-device is online with ip 10.42.42.42"

echo "Stopping smart config"
kill $smartconfig_pid &>/dev/null
wait $! 2>/dev/null

echo "Fetching firmware backup"
sleep 2
timestamp=`date +%Y%m%d_%H%M%S`
mkdir -p "../backups/$timestamp"
pushd "../backups/$timestamp" >/dev/null
curl -JO http://10.42.42.42/backup

echo "======================================================"
echo "Getting Info from IoT-device"
curl http://10.42.42.42 2> /dev/null | tee device-info.txt
popd >/dev/null

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
echo "A basic build of Sonoff-Tasmota v6.5.0 is already included in this repository."
echo "   # curl http://10.42.42.42/flash3"
echo "Alternatively let the device download and flash a file via HTTP:"
echo "   # curl http://10.42.42.42/flash3?url=http://10.42.42.1/files/thirdparty.bin"
echo
echo "HAVE FUN!"
echo "======================================================"
read -p "Do you want to flash another device? [y/N] " -n 1 -r
echo
done

echo "Exiting..."

popd >/dev/null

