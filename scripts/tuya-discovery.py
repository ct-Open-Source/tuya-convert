#!/usr/bin/env python3
# encoding: utf-8
"""
tuya-discovery.py
Created by kueblc on 2019-11-13.
Discover Tuya devices on the LAN via UDP broadcast
"""

import asyncio
import json

from Cryptodome.Cipher import AES
pad = lambda s: s + (16 - len(s) % 16) * chr(16 - len(s) % 16)
unpad = lambda s: s[:-ord(s[len(s) - 1:])]
encrypt = lambda msg, key: AES.new(key.encode(), AES.MODE_ECB).encrypt(pad(msg).encode())
decrypt = lambda msg, key: unpad(AES.new(key.encode(), AES.MODE_ECB).decrypt(msg.encode()))

from hashlib import md5
udpkey = md5(b"yGAdlopoPVldABfn").digest()
decrypt_udp = lambda msg: decrypt(msg, udpkey)

class TuyaDiscovery(asyncio.DatagramProtocol):
	def datagram_received(self, data, addr):
		# remove message frame
		data = data[20:-8]
		# decrypt if encrypted
		try:
			data = decrypt_udp(data)
		except:
			pass
		# parse json
		try:
			data = json.loads(data)
		except:
			pass
		print(addr[0], data)

def main():
	loop = asyncio.get_event_loop()
	listener = loop.create_datagram_endpoint(TuyaDiscovery, local_addr=('0.0.0.0', 6666))
	encrypted_listener = loop.create_datagram_endpoint(TuyaDiscovery, local_addr=('0.0.0.0', 6667))
	loop.run_until_complete(listener)
	print("Listening for Tuya broadcast on UDP 6666")
	loop.run_until_complete(encrypted_listener)
	print("Listening for encrypted Tuya broadcast on UDP 6667")
	try:
		loop.run_forever()
	except KeyboardInterrupt:
		loop.stop()

if __name__ == "__main__":
	main()

