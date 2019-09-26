#!/bin/sh

# Source config
. ../config.txt

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
	echo "Backing up NetworkManager.conf..."
	sudo cp -n /etc/NetworkManager/NetworkManager.conf /etc/NetworkManager/NetworkManager.conf.backup

	sudo bash -c 'cat <<- EOF > /etc/NetworkManager/NetworkManager.conf
		[main]
		plugins=keyfile

		[keyfile]
		unmanaged-devices=interface-name:$WLAN
	EOF'

	echo "Restarting NetworkManager..."
	sudo service network-manager restart
fi
sudo ifconfig $WLAN up

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
sudo ifconfig $WLAN up 10.42.42.1 netmask 255.255.255.0
echo "Applying iptables rules..."
sudo iptables --flush
sudo iptables --table nat --flush
sudo iptables --delete-chain
sudo iptables --table nat --delete-chain
sudo iptables --table nat --append POSTROUTING --out-interface $ETH -j MASQUERADE
sudo iptables --append FORWARD --in-interface $WLAN -j ACCEPT

echo "Starting DNSMASQ server..."
sudo dnsmasq \
	--no-resolv \
	--interface=$WLAN \
	--bind-interfaces \
	--listen-address=10.42.42.1 \
	--dhcp-range=10.42.42.10,10.42.42.40,12h \
	--server=9.9.9.9 \
	--server=1.1.1.1 \
	--address=/#/10.42.42.1

sudo sysctl -w net.ipv4.ip_forward=1 > /dev/null 2>&1

sudo ip route add 255.255.255.255 dev $WLAN


echo "Starting AP on $WLAN..."
sudo hostapd hostapd.conf
echo "AP closed"

if test -d /etc/NetworkManager; then
	echo "Restoring NetworkManager.conf..."
	sudo mv /etc/NetworkManager/NetworkManager.conf.backup /etc/NetworkManager/NetworkManager.conf
	sudo service network-manager restart
fi
echo "Stopping DNSMASQ server..."
sudo pkill dnsmasq
sudo iptables --flush
sudo iptables --flush -t nat
sudo iptables --delete-chain
sudo iptables --table nat --delete-chain
