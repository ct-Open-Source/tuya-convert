FROM phusion/baseimage:0.11

RUN apt-get update && apt-get install -y git sudo iptables iproute2 iputils-ping

RUN echo '* libraries/restart-without-asking boolean true' | sudo debconf-set-selections

COPY docker/bin /usr/bin/

COPY . /usr/bin/tuya-convert

RUN cd /usr/bin/tuya-convert && ./install_prereq.sh

RUN mkdir -p /etc/service/tuya && cd /etc/service/tuya && ln -s /usr/bin/config.sh run
