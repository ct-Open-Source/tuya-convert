#!/usr/bin/env python3
# encoding: utf-8
"""
main.py
Created by kueblc on 2019-01-25.
Configure Tuya devices via smartconfig for tuya-convert
"""

ssid = "vtrust-flash"
passwd = ""
region = "US"
token = "00000000"
secret = "0101"

from smartconfig import smartconfig
from time import sleep

print('Put device in EZ config mode (blinking fast)')
print('Sending SSID                  '+ssid)
print('Sending wifiPassword          '+passwd)
print('Sending token                 '+token)
print('Sending secret                '+secret)

for i in range(10): # Make 10 attempts

	smartconfig( passwd, ssid, region, token, secret )

	print()
	print('SmartConfig complete.')

	for t in range(3, 0, -1):
		print('Auto retry in %ds. ' % t, end='', flush=True)
		sleep(1)
		print(end='\r')

	print('Resending SmartConfig Packets')
