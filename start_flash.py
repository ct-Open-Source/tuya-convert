#!/usr/bin/python3
# encoding: utf-8
"""
start_flash.py

Created by Merlin Schumacher (merlin.schumacher@gmail.com) for c't Magazin
"""

import disclaimer, network, config

def prepare_system():
    wifi_device, eth_device, ap_ssid, ap_password = config.get()
    network.set_wifi_management(wifi_device, False)
    network.start_ap(wifi_device, ap_ssid, ap_password)
    network.configure_iptables(wifi_device, eth_device)

if __name__ == "__main__":
    disclaimer.show()
    disclaimer.acknowledge()
    prepare_system()


