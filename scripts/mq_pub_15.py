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

help_message = '''USAGE:
	"-i"/"--deviceID"
	"-l"/"--localKey" [default=0000000000000000]
	"-b"/"--broker" [default=127.0.0.1]
iot:	
%s -i 43511212112233445566 -l a1b2c3d4e5f67788''' % (sys.argv[0].split("/")[-1])

class iotAES(object):
    def __init__(self, key):
        self.bs = 16
        self.key = key
    def encrypt(self, raw):
        _ = self._pad(raw)
        cipher = pyaes.blockfeeder.Encrypter(pyaes.AESModeOfOperationECB(self.key))
        crypted_text = cipher.feed(raw)
        crypted_text += cipher.feed()
        crypted_text_b64 = base64.b64encode(crypted_text)
        return crypted_text_b64
    def decrypt(self, enc):
        enc = base64.b64decode(enc)
        cipher = pyaes.blockfeeder.Decrypter(pyaes.AESModeOfOperationECB(self.key))
        plain_text = cipher.feed(enc)
        plain_text += cipher.feed()
        return plain_text
    def _pad(self, s):
        padnum = self.bs - len(s) % self.bs
        return s + padnum * chr(padnum).encode()
    @staticmethod
    def _unpad(s):
        return s[:-ord(s[len(s)-1:])]
def iot_dec(message, local_key):
	iot_aes = iotAES(local_key)
	message_clear = iot_aes.decrypt(message[19:])
	print (message_clear)
	return message_clear
def iot_enc(message, local_key):
	iot_aes = iotAES(local_key)
	messge_enc = iot_aes.encrypt(message)
	m = md5()
	PROTOCOL_VERSION_BYTES = b'2.1'
	#	preMd5String = b'data=' + messge_enc + b'||lpv=' + PROTOCOL_VERSION_BYTES + b'||' + local_key
	preMd5String = b'data=' + messge_enc + b'||pv=' + PROTOCOL_VERSION_BYTES + b'||' + local_key
	#	print (preMd5String)
	m.update(preMd5String)
	md5sum = m.hexdigest()
	print (md5sum) #ca2b66d33d3f50a1 #ca2b66d33d3f50a1
	messge_enc = PROTOCOL_VERSION_BYTES + md5sum[8:][:16].encode('latin1') + messge_enc
	print (messge_enc)
	return messge_enc

class Usage(Exception):
	def __init__(self, msg):
		self.msg = msg

def main(argv=None):
	broker='127.0.0.1'
	localKey = "0000000000000000"
	deviceID = ""
	if argv is None:
		argv = sys.argv
	try: #getopt
		try:
			opts, args = getopt.getopt(argv[1:], "hl:i:vb:", ["help", "localKey=", "deviceID=", "broker="])
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

		if (len(localKey)<10):
			raise Usage(help_message)
		if (len(deviceID)<10):
			raise Usage(help_message) #
	except Usage:
		print (sys.argv[0].split("/")[-1] + ": ")
		print ("\t for help use --help")
		print (help_message)
		return 2
	
	message = '{"data":{"gwId":"%s"},"protocol":15,"s":%d,"t":%d}'  %(deviceID, 1523715, time.time())
	m1 = iot_enc(message, localKey)

	client = mqtt.Client("P1")
	client.connect(broker)
	client.publish("smart/device/in/%s" % (deviceID), m1)
	client.disconnect()

if __name__ == "__main__":
	sys.exit(main())
