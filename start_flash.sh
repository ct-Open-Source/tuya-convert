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

. ./setup_checks.sh

echo "======================================================"
echo -n "  Starting AP in a screen"
$screen_with_log smarthack-wifi.log -S smarthack-wifi -m -d ./setup_ap.sh
while ! ping -c 1 -W 1 -n $GATEWAY &> /dev/null; do
	printf .
done
echo
sleep 5
echo "  Starting web server in a screen"
$screen_with_log smarthack-web.log -S smarthack-web -m -d ./fake-registration-server.py
echo "  Starting Mosquitto in a screen"
$screen_with_log smarthack-mqtt.log -S smarthack-mqtt -m -d mosquitto -v
echo "  Starting PSK frontend in a screen"
$screen_with_log smarthack-psk.log -S smarthack-psk -m -d ./psk-frontend.py -v
echo "  Starting Tuya Discovery in a screen"
$screen_with_log smarthack-udp.log -S smarthack-udp -m -d ./tuya-discovery.py
echo
REPLY=y
while [[ $REPLY =~ ^[Yy]$ ]]; do
echo "======================================================"
echo
echo "IMPORTANT"
echo "1. Connect any other device (a smartphone or something) to the WIFI $AP"
echo "   This step is IMPORTANT otherwise the smartconfig will not work!"
echo "2. Put your IoT device in autoconfig/smartconfig/pairing mode (LED will blink fast). This is usually done by pressing and holding the primary button of the device"
echo "3. Press ${bold}ENTER${normal} to continue"
read x
echo ""
echo "======================================================"

echo "Starting smart config pairing procedure"
./smartconfig/main.py &

echo "Waiting for the device to install the intermediate firmware"

i=120
while ! ping -c 1 -W 1 -n 10.42.42.42 &> /dev/null; do
	printf .
	if (( --i == 0 )); then
		echo
		echo "Device did not appear with the intermediate firmware"
		echo "Check the *.log files in the scripts folder"
		pkill -f smartconfig/main.py && echo "Stopping smart config"
		read -p "Do you want to try flashing another device? [y/N] " -n 1 -r
		echo
		continue 2
	fi
done

echo
echo "IoT-device is online with ip 10.42.42.42"

pkill -f smartconfig/main.py && echo "Stopping smart config"

echo "Fetching firmware backup"
sleep 2
timestamp=`date +%Y%m%d_%H%M%S`
mkdir -p "../backups/$timestamp"
pushd "../backups/$timestamp" >/dev/null
curl -JO http://10.42.42.42/backup

echo "======================================================"
echo "Getting Info from IoT-device"
curl -s http://10.42.42.42 | tee device-info.txt
popd >/dev/null

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
echo "A build of Tasmota v7.0.0.3 is already included in this repository."
echo "   # curl http://10.42.42.42/flash3"
echo "If you want to flash the included ESPurna 1.13.5 image use this command:"
echo "   # curl http://10.42.42.42/flash3?url=http://10.42.42.1/files/espurna-base.bin"
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

