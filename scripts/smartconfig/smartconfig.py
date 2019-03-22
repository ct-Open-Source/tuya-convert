#!/usr/bin/env python3
# encoding: utf-8
"""
smartconfig.py
Created by kueblc on 2019-01-25.
Configure Tuya devices via smartconfig without the Tuya cloud or app
broadcast strategy ported from https://github.com/tuyapi/link
multicast strategy reverse engineered by kueblc
"""

# Defaults

# time to sleep inbetween packets, 5ms
GAP = 5 / 1000.

BIND_ADDRESS = '10.42.42.1'

MULTICAST_TTL = 1

from socket import *
from time import sleep

class SmartConfigSocket(object):
	def __init__( self, address = BIND_ADDRESS, gap = GAP ):
		self._socket = socket(AF_INET, SOCK_DGRAM, IPPROTO_UDP)
		self._socket.setsockopt(SOL_SOCKET, SO_REUSEADDR, 1)
		self._socket.setsockopt(SOL_SOCKET, SO_BROADCAST, 1)
		self._socket.setsockopt(IPPROTO_IP, IP_MULTICAST_TTL, MULTICAST_TTL)
		self._socket.bind((address, 0))
		self._gap = gap

	def send_broadcast( self, data ):
		for length in data:
			self._socket.sendto( b'\0' * length, ('255.255.255.255', 30011))
			sleep(self._gap)

	def send_multicast( self, data ):
		for ip in data:
			self._socket.sendto( b'\0', (ip, 30012))
			sleep(self._gap)

from broadcast import broadcast_head, encode_broadcast_body
from multicast import multicast_head, encode_multicast_body

def smartconfig( password, ssid, region, token, secret ):
	sock = SmartConfigSocket()
	token_group = region + token + secret
	broadcast_body = encode_broadcast_body( password, ssid, token_group )
#	print(broadcast_body)
	multicast_body = encode_multicast_body( password, ssid, token_group )
#	print(multicast_body)
#	print("sending header")
	for i in range(40): # originally 143, that's more than we really need
		sock.send_multicast(multicast_head)
		sock.send_broadcast(broadcast_head)
	for i in range(10): # originally 30, again, more than necessary
#		print("sending body iteration " + str(i))
		print('.', end='', flush=True) # quick and dirty progress meter
		sock.send_multicast(multicast_head)
		sock.send_multicast(multicast_body)
		sock.send_broadcast(broadcast_body)

