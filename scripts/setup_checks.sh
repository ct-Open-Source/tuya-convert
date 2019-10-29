#!/bin/bash

# Source config
. ../config.txt

check_config () {
	if ! iw list | grep -q "* AP"; then
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
}

check_port () {
	protocol="$1"
	port="$2"
	reason="$3"
	echo -n "Checking ${protocol^^} port $port... "
	process_pid=$(sudo ss -Hlnp -A "$protocol" "sport = :$port" | grep -Po "(?<=pid=)(\d+)" | head -n1)
	if [ -n "$process_pid" ]; then
		process_name=$(ps -p "$process_pid" -o comm=)
		echo "Occupied by $process_name with PID $process_pid."
		echo "Port $port is needed to $reason"
		read -p "Do you wish to terminate $process_name? [y/N] " -n 1 -r
		if [[ ! $REPLY =~ ^[Yy]$ ]]; then
			echo "Aborting due to occupied port"
			exit 1
		else
			echo "Attempting to terminate $process_name with PID $process_pid"
			service=$(sudo ps -p "$process_pid" -o unit | grep service)
			if [ -n "$service" ]; then
				sudo systemctl stop "$service"
			else
				sudo kill -9 "$process_pid"
			fi
			sleep 1
		fi
	else
		echo "Available."
	fi
}

check_config
check_port udp 53 "resolve DNS queries"
check_port tcp 80 "answer HTTP requests"
check_port tcp 443 "answer HTTPS requests"
check_port tcp 1883 "run MQTT"
check_port tcp 8886 "run MQTTS"

