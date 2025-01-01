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

# If Debian 12 (Bookworm) or newer use this
debian12Install() {
        sudo apt-get update
        sudo apt-get install -y git iw dnsmasq rfkill hostapd screen curl build-essential python3-pip python3-setuptools python3-wheel python3-dev mosquitto haveged net-tools libssl-dev iproute2 iputils-ping
        # Run the following command from the root folder of each project to create a virtual environment configuration folder:
        python3 -m venv ./python3env
        # Run the following command from the root of the project to start using the virtual environment:
        source ./python3env/bin/activate
        # Now install Python libraries into a virtual environment (venv):
        pip install --upgrade paho-mqtt tornado git+https://github.com/drbild/sslpsk.git pycryptodomex
        # To leave the virtual environment, run the following command from any directory:
        deactivate
}

if [[ -e /etc/os-release ]]; then
        source /etc/os-release
else
        echo "/etc/os-release not found! Assuming debian-based system, but this will likely fail!"
        ID=debian
fi

# Check if Debian 12 (Bookworm) or newer
if [[ ${ID} == 'debian' ]] && [[ ${VERSION_ID} -ge 12 ]] then
        # Yes, Debian 12 (Bookworm) or newer
        debian12Install
else
        # No, Debian 11 or older or other operating system
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
fi

echo "Ready to start upgrade"
