#!/bin/bash

# Source config
. ../config.txt
if [[ "$WLAN" == "auto" || "$(echo $(iw dev | grep "Interface ") | grep "$WLAN")" ]]; then
    WLAN=$(echo $(iw dev | grep "Interface ") | cut -d" " -f 2 | head -1)
    echo "Wireless interface autodetected as $WLAN..."
fi

version_check () {
	echo "System info"
	echo "==========="
	git rev-parse --short HEAD
	uname -a
	openssl version
	dnsmasq --version
	hostapd -v
	/usr/bin/env python3 --version
	echo "==========="
}

setup () {
	rfkill unblock wifi

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
	sudo ip link set $WLAN down
	sudo ip addr add $GATEWAY/24 dev $WLAN
	sudo ip link set $WLAN up
	sudo ip route add 10.42.42.0/24 dev $WLAN src $GATEWAY
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

	# Read hostapd.conf with interface from stdin for
	# backward compatibility (hostapd < v2.6). See #398
	(cat hostapd.conf
     echo "interface=$WLAN"
     if [[ ! -z "$WPA_PASS" ]]; then
         echo wpa=2
         echo wpa_passphrase="$WPA_PASS"
         echo wpa_key_mgmt=WPA-PSK
         echo wpa_pairwise=TKIP
         echo rsn_pairwise=CCMP
     fi) | sudo hostapd /dev/stdin
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

version_check
trap cleanup EXIT
setup

