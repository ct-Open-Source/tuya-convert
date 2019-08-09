#!/usr/bin/python3
# encoding: utf-8

import configparser

def fail():
    print("Please check the config.ini for valid data")
    quit()

def get():
    config = configparser.ConfigParser()
    config.read('config.ini')
    if not 'TuyaHack' in config:
        fail()
    wifi_device = config['TuyaHack']['WLAN']
    eth_device = config['TuyaHack']['ETH']
    ap_ssid = config['TuyaHack']['AP']
    ap_password = config['TuyaHack']['PASS']
    return wifi_device,eth_device,ap_ssid,ap_password
