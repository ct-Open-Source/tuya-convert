#!/usr/bin/env python3
# encoding: utf-8
"""
mq_pub_15.py
Created by nano on 2018-11-22.
Copyright (c) 2018 VTRUST. All rights reserved.
"""
import sys, getopt, time, pyaes, base64
import paho.mqtt.client as mqtt  #pip install paho-mqtt
from hashlib import md5
import binascii

help_message = '''USAGE:
	"-i"/"--deviceID"
	"-l"/"--localKey" [default=0000000000000000]
	"-b"/"--broker" [default=127.0.0.1]
	"-p"/"--protocol" [default=2.1]
iot:	
%s -i 43511212112233445566 -l a1b2c3d4e5f67788''' % (sys.argv[0].split("/")[-1])

class iotAES(object):
    def __init__(self, key):
        self.bs = 16
        self.key = key
    def encrypt(self, raw):
        _ = self._pad(raw)
        cipher = pyaes.blockfeeder.Encrypter(pyaes.AESModeOfOperationECB(self.key.encode()))
        crypted_text = cipher.feed(raw)
        crypted_text += cipher.feed()
        return crypted_text
    def decrypt(self, enc):
        enc = base64.b64decode(enc)
        cipher = pyaes.blockfeeder.Decrypter(pyaes.AESModeOfOperationECB(self.key))
        plain_text = cipher.feed(enc)
        plain_text += cipher.feed()
        return plain_text
    def _pad(self, s):
        padnum = self.bs - len(s) % self.bs
        return s + padnum * chr(padnum)
    @staticmethod
    def _unpad(s):
        return s[:-ord(s[len(s)-1:])]
def iot_dec(message, local_key):
	iot_aes = iotAES(local_key)
	message_clear = iot_aes.decrypt(message[19:])
	print (message_clear)
	return message_clear
def iot_enc(message, local_key, protocol):
	iot_aes = iotAES(local_key)
	messge_enc = iot_aes.encrypt(message)
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

	client = mqtt.Client("P1")
	client.connect(broker)
	client.publish("smart/device/in/%s" % (deviceID), m1)
	client.disconnect()

if __name__ == "__main__":
	sys.exit(main())
