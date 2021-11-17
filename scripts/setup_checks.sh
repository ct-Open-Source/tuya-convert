#!/bin/bash

# Source config
. ../config.txt

check_eula () {
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
}

check_config () {
	if ! iw list | grep -A 10 "Supported interface modes" | grep -q -e "\* AP$"; then
		echo "AP mode not supported!"
		echo "Please attach a WiFi card that supports AP mode."
		exit 1
	fi

	echo -n "Checking for network interface $WLAN... "
	if [ -e /sys/class/net/$WLAN ]; then
		echo "Found."
	else
		echo "Not found!"
		echo -n "Please edit WLAN in config.txt to one of: "
		ls -m /sys/class/net
		exit 1
	fi

	if [ -n "$SSH_CONNECTION" ]; then
		remoteip=$(echo "$SSH_CONNECTION" | cut -d " " -f1)
		if ip -o route get $remoteip | grep -q " dev $WLAN "; then
			echo "Warning: It appears that you are running this script over an SSH connection"
			echo "that uses the WiFi interface $WIFI. This interface will be reconfigured to run"
			echo "in access point (AP) mode, at which time all connections will be dropped."
			echo "If you continue, your SSH connection will be dropped and you can likely no longer"
			echo "interact with this script. To avoid this, connect via wired ethernet or USB."
			read -p "Continue? [y/N]" -n 1 -r
			echo
			if [[ ! $REPLY =~ ^[Yy]$ ]]; then
				exit
			fi
		fi
	fi
}

check_port () {
	protocol="$1"
	port="$2"
	reason="$3"
	echo -n "Checking ${protocol^^} port $port... "
	ss_output=$(sudo ss -lnp -A "$protocol" "sport = :$port")
	process_pid=$(echo "$ss_output" | grep -Po "(?<=pid=)(\d+)" | head -n1)
	if [ -n "$process_pid" ]; then
		process_name=$(ps -p "$process_pid" -o comm=)
		echo "Occupied by $process_name with PID $process_pid."
		echo "Port $port is needed to $reason"
		read -p "Do you wish to terminate $process_name? [y/N] " -n 1 -r
		echo
		if [[ "$REPLY" =~ ^[Ss]$ ]]; then
			echo "Skipping..."
			return
		fi
		if [[ ! $REPLY =~ ^[Yy]$ ]]; then
			echo "Aborting due to occupied port"
			exit 1
		else
			service=$(ps -p "$process_pid" -o unit= | grep .service | grep -Ev ^user)
			if [ -n "$service" ]; then
				echo "Attempting to stop $service"
				sudo systemctl stop "$service"
			else
				echo "Attempting to terminate $process_name"
				sudo kill "$process_pid"
				if ! sudo timeout 10 tail --pid="$process_pid" -f /dev/null; then
					echo "$process_name is still running after 10 seconds, sending SIGKILL"
					sudo kill -9 "$process_pid"
					sudo tail --pid="$process_pid" -f /dev/null
				fi
			fi
			sleep 1
		fi
	else
		if [ $(echo "$ss_output" | wc -l) -gt 1 ]; then
			echo "Occupied by unknown process."
			echo "Port $port is needed to $reason"
			echo "Aborting due to occupied port"
			exit 1
		fi
		echo "Available."
	fi
}

check_firewall () {
	if sudo systemctl stop firewalld.service &>/dev/null; then
		echo "Attempting to stop firewalld.service"
		echo "When done, enable with: ${bold}sudo systemctl start firewalld.service${normal}"
	fi
	if command -v ufw >/dev/null && sudo ufw status | grep -qw active; then
		sudo ufw disable
		echo "When done, enable with: ${bold}sudo ufw enable${normal}"
	fi
}

check_blacklist () {
	if [ -e /etc/modprobe.d/blacklist-rtl8192cu.conf ]; then
		echo "Detected /etc/modprobe.d/blacklist-rtl8192cu.conf"
		echo "This has been known to cause kernel panic in hostapd"
		echo "See https://github.com/ct-Open-Source/tuya-convert/issues/373"
		read -p "Do you wish to remove this file? [y/N] " -n 1 -r
		echo
		if [[ $REPLY =~ ^[Yy]$ ]]; then
			sudo rm /etc/modprobe.d/blacklist-rtl8192cu.conf
		fi
	fi
}

check_eula
check_config
check_port udp 53 "resolve DNS queries"
check_port udp 67 "offer DHCP leases"
check_port tcp 80 "answer HTTP requests"
check_port tcp 443 "answer HTTPS requests"
check_port udp 6666 "detect unencrypted Tuya firmware"
check_port udp 6667 "detect encrypted Tuya firmware"
check_port tcp 1883 "run MQTT"
check_port tcp 8886 "run MQTTS"
check_firewall
check_blacklist

