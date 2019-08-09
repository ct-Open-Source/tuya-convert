#!/usr/bin/python3
# encoding: utf-8

import NetworkManager, dbus, iptc
from shutil import copyfile
from subprocess import Popen, PIPE, STDOUT

dbus = dbus.SystemBus()
systemd = dbus.get_object('org.freedesktop.systemd1', '/org/freedesktop/systemd1')
manager = dbus.Interface(systemd1, 'org.freedesktop.systemd1.Manager')

c = NetworkManager.const

def set_wifi_management(wifi_device, state):
    for dev in NetworkManager.NetworkManager.GetDevices():
        dev.Managed = False

def configure_hostapd(wifi_device, ap_ssid, ap_password):
    config_data = """
interface="""+wifi_device+"""
driver=nl80211
ssid="""+ap_ssid+"""
hw_mode=g
channel=1
macaddr_acl=0
auth_algs=1
ignore_broadcast_ssid=0
wpa=2
wpa_passphrase="""+ap_password+"""
wpa_key_mgmt=WPA-PSK
wpa_pairwise=TKIP
rsn_pairwise=CCMP"""

    with open("hostapd-tuya.conf", "wt") as hostap_conf
        hostap_conf.write(config_data)
        hostap_conf.close()
    
def configure_dnsmasq(wifi_device):
    config_data = """
# disables dnsmasq reading any other files like /etc/resolv.conf for nameservers
no-resolv
# Interface to bind to
interface="""+wifi_device+"""
#Specify starting_range,end_range,lease_time
dhcp-range=10.42.42.10,10.42.42.40,12h
# dns addresses to send to the clients
server=9.9.9.9
server=1.1.1.1
address=/tuya.com/10.42.42.1
address=/tuyaeu.com/10.42.42.1
address=/tuyaus.com/10.42.42.1
address=/tuyacn.com/10.42.42.1"""

    with open("dnsmasq-tuya.conf", "wt") as dnsmasq_conf
        dnsmasq_conf.write(config_data)
        dnsmasq_conf.close()

def start_ap(wifi_device, ap_ssid, ap_password):
    configure_hostapd(wifi_device, ap_ssid, ap_password)
    configure_dnsmasq(wifi_device)
    dnsmasq_job = manager.StopUnit('dnsmasq.service', 'replace')
    hostap_job = manager.StopUnit('hostapd.service', 'replace')
    subprocess.run(["hostapd", "hostapd-tuya.conf"], check=True)
    subprocess.run(["dnsmasq", "-C", "hostapd-tuya.conf"], check=True)
    subprocess.run(["ifconfig", wifi-device, "up 10.42.42.1 netmask 255.255.255.0"], check=True)

def configure_iptables():
    ipt_input = iptc.tables(iptc.Table.INPUT)
    ipt_forward = iptc.tables(iptc.Table.FORWARD)
    ipt_output = iptc.tables(iptc.Table.OUTPUT)
    ipt_nat = iptc.tables(iptc.Table.NAT)

    ipt_input.flush()
    ipt_forward.flush()
    ipt_output.flush()
    ipt_nat.flush()

    ipt_chain_postrouting = ipt_nat.append





def stop_ap():
