#!/usr/bin/python3
# encoding: utf-8
"""
backup.py

Created by nano on 2019-01-10.
Copyright (c) 2019 VTRUST GmbH. All rights reserved.
"""

import sys
import os
import http.client
from binascii import unhexlify
import datetime

DEVICE_IP = "10.42.42.42"


def main():
	print("Create backup of entire FLASH from %s" % DEVICE_IP )
	data = b""
	conn = http.client.HTTPConnection(DEVICE_IP)
	conn.request("GET","/flashsize")
	flashsize = int(conn.getresponse().read())
	print("Connected... Flashsize=",flashsize)
	for address in range(0,flashsize,1024):
		conn.request("GET", "/get?read=%X" % address )
		r1 = conn.getresponse()
#		print(r1.status, r1.reason)
		block = r1.read().split(b'\n')
		print(block[0])
		data += block[1]
	conn.close()
	bindata = unhexlify(data)
	f= open(datetime.datetime.now().strftime("../%Y-%m-%d_%H-%M-%S_readout.bin"),"wb")
	f.write(bindata)
	f.close
	pass


if __name__ == '__main__':
	main()


