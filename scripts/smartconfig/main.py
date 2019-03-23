#!/usr/bin/env python3
# encoding: utf-8
"""
main.py
Created by kueblc on 2019-01-25.
Configure Tuya devices via smartconfig for tuya-convert
"""

ssid = "vtrust-flash"
passwd = "flashmeifyoucan"
region = "US"
token = "00000000"
secret = "0101"

from smartconfig import smartconfig

print('Put Device in Learn Mode! Sending SmartConfig Packets now')

print('Sending SSID                  '+ssid)
print('Sending wifiPassword          '+passwd)
print('SmartConfig in progress')

smartconfig( passwd, ssid, region, token, secret )

print()
print('SmartConfig complete.')

