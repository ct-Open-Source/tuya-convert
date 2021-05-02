FROM alpine:3.13

RUN apk add --update bash git iw dnsmasq hostapd screen curl py3-pip py3-wheel python3-dev mosquitto haveged net-tools openssl openssl-dev gcc musl-dev linux-headers sudo coreutils grep iproute2

RUN python3 -m pip install --upgrade paho-mqtt tornado git+https://github.com/drbild/sslpsk.git pycryptodomex

COPY docker/bin /usr/bin/

COPY . /usr/bin/tuya-convert

WORKDIR "/usr/bin/tuya-convert"

ENTRYPOINT ["tuya-start"]
