#!/bin/sh

# Source config
. ../config.txt

if test -d /etc/NetworkManager; then
    STATE_DEV_WLAN=$( nmcli device show $WLAN | sed 's/^GENERAL.STATE: *\(.*\)$/\1/p;d' )

    if [ "$STATE_DEV_WLAN" != "10 (unmanaged)" ]; then
	nmcli set $WLAN managed no
    fi
fi
sudo ifconfig $WLAN up

DIR_DNSMASQ_CONF=$(mktemp -d )

echo "Writing dnsmasq config file..."
echo "Creating new ${DIR_DNSMASQ_CONF}/dnsmasq.conf..."
cat <<- EOF > ${DIR_DNSMASQ_CONF}/dnsmasq.conf
	# disables dnsmasq reading any other files like /etc/resolv.conf for nameservers
	no-resolv
	# Interface to bind to
	interface=$WLAN
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
sudo dnsmasq --conf-dir ${DIR_DNSMASQ_CONF}

sudo sysctl -w net.ipv4.ip_forward=1 > /dev/null 2>&1

sudo ip route add 255.255.255.255 dev $WLAN


echo "Starting AP on $WLAN in screen terminal..."
sudo hostapd /etc/hostapd/hostapd.conf

if test -d /etc/NetworkManager; then
	sudo service network-manager restart
fi
sudo /etc/init.d/dnsmasq stop > /dev/null 2>&1
sudo pkill dnsmasq
sudo rm /etc/dnsmasq.hosts > /dev/null 2>&1
sudo iptables --flush
sudo iptables --flush -t nat
sudo iptables --delete-chain
sudo iptables --table nat --delete-chain
