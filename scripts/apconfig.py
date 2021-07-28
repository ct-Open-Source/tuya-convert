#!/usr/bin/env python3
# encoding: utf-8
"""
apconfig.py
Created by kueblc on 2021-07-20.
Configure Tuya devices via AP config without the Tuya cloud or app
"""

# Defaults
BIND_ADDRESS = '0.0.0.0'
SSID = 'vtrust-flash'
MULTICAST_TTL = 1

from binascii import crc32

import json
jsonstr = lambda j : json.dumps(j, separators=(',', ':'))

int_to_bytes = lambda i : i.to_bytes(4, byteorder='big')

FRAME_PREFIX = b'\x00\x00\x55\xaa'
FRAME_SUFFIX = b'\x00\x00\xaa\x55'
COMMAND_AP_CONFIG = 1

from socket import *

class ApConfigSocket(object):
	def __init__ (self, address = BIND_ADDRESS):
		self._socket = socket(AF_INET, SOCK_DGRAM, IPPROTO_UDP)
		self._socket.setsockopt(SOL_SOCKET, SO_REUSEADDR, 1)
		self._socket.setsockopt(SOL_SOCKET, SO_BROADCAST, 1)
		self._socket.setsockopt(IPPROTO_IP, IP_MULTICAST_TTL, MULTICAST_TTL)
		self._socket.bind((address, 0))

	def send (self, data):
		self._socket.sendto(data, ('255.255.255.255', 6669))

def encode_tuya_frame (command, payload, sequence = 0):
	message = FRAME_PREFIX + \
		int_to_bytes(sequence) + \
		int_to_bytes(command) + \
		int_to_bytes(len(payload) + 8) + \
		payload
	return message + int_to_bytes(crc32(message)) + FRAME_SUFFIX

def ap_config (ssid, passwd = "", token = "00000000"):
	payload = jsonstr({
		"ssid": ssid,
		"passwd": passwd,
		"token": token
	}).encode()
	return encode_tuya_frame(COMMAND_AP_CONFIG, payload)

def send_ap_config ():
	packet = ap_config(SSID)
	print("Sending " + packet.hex())
	sock = ApConfigSocket()
	sock.send(packet)

send_ap_config()

