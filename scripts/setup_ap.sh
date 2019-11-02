#!/bin/bash

# Source config
. ../config.txt

setup () {
	wpa_supplicant_pid=$(pidof wpa_supplicant)
	if [ -n "$wpa_supplicant_pid" ]; then
		echo "Attempting to stop wpa_supplicant"
		sudo kill $wpa_supplicant_pid
	fi

	if test -d /etc/NetworkManager; then
		echo "Stopping NetworkManager..."
		sudo service network-manager stop
	fi

	echo "Configuring AP interface..."
	sudo ifconfig $WLAN down
	sudo ifconfig $WLAN up $GATEWAY netmask 255.255.255.0
	sudo ip route add 255.255.255.255 dev $WLAN

	echo "Starting DNSMASQ server..."
	sudo dnsmasq \
		--no-resolv \
		--interface=$WLAN \
		--bind-interfaces \
		--listen-address=$GATEWAY \
		--dhcp-range=10.42.42.10,10.42.42.40,12h \
		--address=/#/$GATEWAY

	echo "Starting AP on $WLAN..."
	sudo hostapd hostapd.conf -i $WLAN
}

cleanup () {
	sudo pkill hostapd
	echo "AP closed"

	echo "Stopping DNSMASQ server..."
	sudo pkill dnsmasq

	if test -d /etc/NetworkManager; then
		echo "Restarting NetworkManager..."
		sudo service network-manager restart
	fi
}

trap cleanup EXIT
setup

