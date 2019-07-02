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
	echo "Backing up NetworkManager.cfg..."
	sudo cp -n /etc/NetworkManager/NetworkManager.conf /etc/NetworkManager/NetworkManager.conf.backup

	cat <<- EOF > /etc/NetworkManager/NetworkManager.conf
		[main]
		plugins=keyfile

		[keyfile]
		unmanaged-devices=interface-name:$WLAN
	EOF

	echo "Restarting NetworkManager..."
	sudo service network-manager restart
fi
sudo ifconfig $WLAN up

echo "Backing up /etc/dnsmasq.conf..."
sudo cp -n /etc/dnsmasq.conf /etc/dnsmasq.conf.backup


echo "Writing dnsmasq config file..."
echo "Creating new /etc/dnsmasq.conf..."
cat <<- EOF >/etc/dnsmasq.conf
	# disables dnsmasq reading any other files like /etc/resolv.conf for nameservers
	no-resolv
	# Interface to bind to
	interface=$WLAN
	bind-interfaces
	listen-address=10.42.42.1
	#Specify starting_range,end_range,lease_time
	dhcp-range=10.42.42.10,10.42.42.40,12h
	# dns addresses to send to the clients
	server=9.9.9.9
	server=1.1.1.1
	address=/tuya.com/10.42.42.1
	address=/tuyaeu.com/10.42.42.1
	address=/tuyaus.com/10.42.42.1
	address=/tuyacn.com/10.42.42.1
EOF

echo "Backing up /etc/hostapd/hostapd.conf..."
sudo cp -n /etc/hostapd/hostapd.conf /etc/hostapd/hostapd.conf.backup

echo "Writing hostapd config file..."
cat <<- EOF >/etc/hostapd/hostapd.conf
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
sudo /etc/init.d/dnsmasq stop > /dev/null 2>&1
sudo pkill dnsmasq
sudo dnsmasq

sudo sysctl -w net.ipv4.ip_forward=1 > /dev/null 2>&1

sudo ip route add 255.255.255.255 dev $WLAN


echo "Starting AP on $WLAN in screen terminal..."
sudo hostapd /etc/hostapd/hostapd.conf

if test -d /etc/NetworkManager; then
	sudo mv /etc/NetworkManager/NetworkManager.conf.backup /etc/NetworkManager/NetworkManager.conf
	sudo service network-manager restart
fi
sudo /etc/init.d/dnsmasq stop > /dev/null 2>&1
sudo pkill dnsmasq
sudo mv /etc/dnsmasq.conf.backup /etc/dnsmasq.conf > /dev/null 2>&1
sudo rm /etc/dnsmasq.hosts > /dev/null 2>&1
sudo mv /etc/hostapd/hostapd.conf.backup /etc/hostapd/hostapd.conf > /dev/null 2>&1
sudo iptables --flush
sudo iptables --flush -t nat
sudo iptables --delete-chain
sudo iptables --table nat --delete-chain
