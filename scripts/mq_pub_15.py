#!/usr/bin/env python3
# encoding: utf-8
"""
mq_pub_15.py
Created by nano on 2018-11-22.
Copyright (c) 2018 VTRUST. All rights reserved.
"""
import sys, getopt, time, base64
import paho.mqtt.publish as publish
from hashlib import md5
import binascii

help_message = '''USAGE:
	"-i"/"--deviceID"
	"-l"/"--localKey" [default=0000000000000000]
	"-b"/"--broker" [default=127.0.0.1]
	"-p"/"--protocol" [default=2.1]
iot:	
%s -i 43511212112233445566 -l a1b2c3d4e5f67788''' % (sys.argv[0].split("/")[-1])

from Crypto.Cipher import AES
pad = lambda s: s + (16 - len(s) % 16) * chr(16 - len(s) % 16)
unpad = lambda s: s[:-ord(s[len(s) - 1:])]
encrypt = lambda msg, key: AES.new(key, AES.MODE_ECB).encrypt(pad(msg))
decrypt = lambda msg, key: AES.new(key, AES.MODE_ECB).decrypt(unpad(msg))

def iot_dec(message, local_key):
	message_clear = decrypt(base64.b64decode(message[19:]), local_key)
	print (message_clear)
	return message_clear
def iot_enc(message, local_key, protocol):
	messge_enc = encrypt(message, local_key)
	if protocol == "2.1":
		messge_enc = base64.b64encode(messge_enc)
		signature = b'data=' + messge_enc + b'||pv=' + protocol.encode() + b'||' + local_key.encode()
		signature = md5(signature).hexdigest()[8:8+16].encode()
		messge_enc = protocol.encode() + signature + messge_enc
	else:
		timestamp = b'%08d'%((int(time.time()*100)%100000000))
		messge_enc = timestamp + messge_enc
		crc = binascii.crc32(messge_enc).to_bytes(4, byteorder='big')
		messge_enc = protocol.encode() + crc + messge_enc
	print (messge_enc)
	return messge_enc

class Usage(Exception):
	def __init__(self, msg):
		self.msg = msg

def main(argv=None):
	broker='127.0.0.1'
	localKey = "0000000000000000"
	deviceID = ""
	protocol = "2.1"
	if argv is None:
		argv = sys.argv
	try: #getopt
		try:
			opts, args = getopt.getopt(argv[1:], "hl:i:vb:p:", ["help", "localKey=", "deviceID=", "broker=", "protocol="])
		except:
			raise Usage(help_message)
	
		# option processing
		for option, value in opts:
			if option == "-v":
				verbose = True
			if option in ("-h", "--help"):
				raise Usage(help_message)
			if option in ("-l", "--localKey"):
				localKey = value
			if option in ("-i", "--deviceID"):
				deviceID = value
			if option in ("-b", "--broker"):
				broker = value
			if option in ("-p", "--protocol"):
				protocol = value

		if (len(localKey)<10):
			raise Usage(help_message)
		if (len(deviceID)<10):
			raise Usage(help_message) #
	except Usage:
		print (sys.argv[0].split("/")[-1] + ": ")
		print ("\t for help use --help")
		print (help_message)
		return 2
	
	if protocol == "2.1":
		message = '{"data":{"gwId":"%s"},"protocol":15,"s":%d,"t":%d}'  %(deviceID, 1523715, time.time())
	else:
		message = '{"data":{"gwId":"%s"},"protocol":15,"s":"%d","t":"%d"}'  %(deviceID, 1523715, time.time())
	print("encoding", message, "using protocol", protocol)
	m1 = iot_enc(message, localKey, protocol)

	publish.single("smart/device/in/%s" % (deviceID), m1, hostname=broker)

if __name__ == "__main__":
	sys.exit(main())
