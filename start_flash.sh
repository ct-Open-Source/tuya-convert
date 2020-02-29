#!/bin/bash
bold=$(tput bold)
normal=$(tput sgr0)
. ./config.txt

setup () {
	echo "tuya-convert $(git describe --tags)"
	pushd scripts >/dev/null || exit
	. ./setup_checks.sh
	screen_minor=$(screen --version | cut -d . -f 2)
	if [ "$screen_minor" -gt 5 ]; then
		screen_with_log="sudo screen -L -Logfile"
	elif [ "$screen_minor" -eq 5 ]; then
		screen_with_log="sudo screen -L"
	else
		screen_with_log="sudo screen -L -t"
	fi
	echo "======================================================"
	echo -n "  Starting AP in a screen"
	$screen_with_log smarthack-wifi.log -S smarthack-wifi -m -d ./setup_ap.sh
	while ! ping -c 1 -W 1 -n "$GATEWAY" &> /dev/null; do
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
}

cleanup () {
	echo "======================================================"
	echo "Cleaning up..."
	sudo screen -S smarthack-web          -X stuff '^C'
	sudo screen -S smarthack-mqtt         -X stuff '^C'
	sudo screen -S smarthack-psk          -X stuff '^C'
	sudo screen -S smarthack-udp          -X stuff '^C'
	echo "Closing AP"
	sudo pkill hostapd
	echo "Exiting..."
	popd >/dev/null || exit
}

trap cleanup EXIT
setup

while true; do
	echo "======================================================"
	echo
	echo "IMPORTANT"
	echo "1. Connect any other device (a smartphone or something) to the WIFI $AP"
	echo "   This step is IMPORTANT otherwise the smartconfig may not work!"
	echo "2. Put your IoT device in autoconfig/smartconfig/pairing mode (LED will blink fast). This is usually done by pressing and holding the primary button of the device"
	echo "   Make sure nothing else is plugged into your IoT device while attempting to flash."
	echo "3. Press ${bold}ENTER${normal} to continue"
	read -r
	echo
	echo "======================================================"

	echo "Starting smart config pairing procedure"
	./smartconfig/main.py &

	echo "Waiting for the device to install the intermediate firmware"

	i=120
	# !!! IMPORTANT !!!
	# Did your device get an IP address other than 10.42.42.42?
	# That is because it is not running the intermediate firmware
	# The intermediate firmware will request 10.42.42.42
	# Do NOT change this address!!!
	# It will NOT make it install and will break this script
	while ! ping -c 1 -W 1 -n 10.42.42.42 &> /dev/null; do
		printf .
		if (( --i == 0 )); then
			echo
			echo "Device did not appear with the intermediate firmware"
			echo "Check the *.log files in the scripts folder"
			pkill -f smartconfig/main.py && echo "Stopping smart config"
			read -p "Do you want to try flashing another device? [y/N] " -n 1 -r
			echo
			[[ "$REPLY" =~ ^[Yy]$ ]] || break 2
			continue 2
		fi
	done

	echo
	echo "IoT-device is online with ip 10.42.42.42"

	pkill -f smartconfig/main.py && echo "Stopping smart config"

	echo "Fetching firmware backup"
	sleep 2
	timestamp=$(date +%Y%m%d_%H%M%S)
	backupfolder="../backups/$timestamp"
	mkdir -p "$backupfolder"
	pushd "$backupfolder" >/dev/null || exit

	if ! curl -JOm 90 http://10.42.42.42/backup; then
		echo "Could not fetch a complete backup"
		read -p "Do you want to continue anyway? [y/N] " -n 1 -r
		echo
		[[ "$REPLY" =~ ^[Yy]$ ]] || break
		sleep 2
	fi

	echo "======================================================"
	echo "Getting Info from IoT-device"
	curl -s http://10.42.42.42 | tee device-info.txt
	popd >/dev/null || exit

	echo "======================================================"
	echo "Ready to flash third party firmware!"
	echo
	echo "For your convenience, the following firmware images are already included in this repository:"
	echo "  Tasmota v8.1.0.2 (wifiman)"
	echo "  ESPurna 1.13.5 (base)"
	echo
	echo "You can also provide your own image by placing it in the /files directory"
	echo "Please ensure the firmware fits the device and includes the bootloader"
	echo "MAXIMUM SIZE IS 512KB"

	./firmware_picker.sh
	sudo mv *.log "$backupfolder/"

	echo "======================================================"
	read -p "Do you want to flash another device? [y/N] " -n 1 -r
	echo
	[[ "$REPLY" =~ ^[Yy]$ ]] || break
done

