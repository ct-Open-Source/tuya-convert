#!/bin/sh

# Source config
. ../config.txt

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

wpa_supplicant_pid=$(pidof wpa_supplicant)
if [ -n "$wpa_supplicant_pid" ]; then
	echo "Attempting to stop wpa_supplicant"
	sudo kill $wpa_supplicant_pid
fi

if test -d /etc/NetworkManager; then
	echo "Stopping NetworkManager..."
	sudo service network-manager stop
fi

echo "Writing hostapd config file..."
cat <<- EOF >hostapd.conf
	interface=$WLAN
	driver=nl80211
	ssid=$AP
	hw_mode=g
	channel=1
	macaddr_acl=0
	auth_algs=1
	ignore_broadcast_ssid=0
	wpa=2
	wpa_passphrase=$PASS
	wpa_key_mgmt=WPA-PSK
	wpa_pairwise=TKIP
	rsn_pairwise=CCMP
EOF

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
sudo hostapd hostapd.conf
echo "AP closed"

echo "Stopping DNSMASQ server..."
sudo pkill dnsmasq

if test -d /etc/NetworkManager; then
	echo "Restarting NetworkManager..."
	sudo service network-manager restart
fi
