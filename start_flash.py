#!/usr/bin/python3
# encoding: utf-8
"""
start_flash.py

Created by Merlin Schumacher (merlin.schumacher@gmail.com) for c't Magazin
"""

import configparser, NetworkManager
##local imports
import disclaimer

c = NetworkManager.const
def prepare_network_manager():
    for dev in NetworkManager.NetworkManager.GetDevices():
        print("%-10s %-19s %-20s %s" % (dev.Interface, c('device_state', dev.State), dev.Driver, dev.Managed))

def start_ap():
    prepare_network_manager()

if __name__ == "__main__":
    #load_config()
#    disclaimer.show()
 #   disclaimer.acknowledge()
    start_ap()

