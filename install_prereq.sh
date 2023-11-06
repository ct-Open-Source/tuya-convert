#!/usr/bin/env bash
set -euo pipefail

debianInstall() {
	sudo apt-get update
	sudo apt-get install -y git iw dnsmasq rfkill hostapd screen curl build-essential python3-pip python3-setuptools python3-wheel python3-dev mosquitto haveged net-tools libssl-dev iproute2 iputils-ping
	sudo python3 -m pip install --user --upgrade paho-mqtt tornado git+https://github.com/drbild/sslpsk.git pycryptodomex
}

archInstall() {
	sudo pacman -S --needed git iw dnsmasq hostapd screen curl python-pip python-wheel python-pycryptodomex python-paho-mqtt python-tornado mosquitto haveged net-tools openssl
	sudo python -m pip install --user --upgrade git+https://github.com/drbild/sslpsk.git
}

if [[ -e /etc/os-release ]]; then
	source /etc/os-release
else
	echo "/etc/os-release not found! Assuming debian-based system, but this will likely fail!"
	ID=debian
fi

if [[ ${ID} == 'debian' ]] || [[ ${ID_LIKE-} == 'debian' ]]; then
	debianInstall
elif [[ ${ID} == 'arch' ]] || [[ ${ID_LIKE-} == 'arch' ]]; then
	archInstall
else
	if [[ -n ${ID_LIKE-} ]]; then
		printID="${ID}/${ID_LIKE}"
	else
		printID="${ID}"
	fi
	echo "/etc/os-release found but distribution ${printID} is not explicitly supported. Assuming debian-based system, but this will likely fail!"
	debianInstall
fi

echo "Ready to start upgrade"
