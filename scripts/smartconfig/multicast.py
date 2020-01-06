#!/usr/bin/env python3
# encoding: utf-8
"""
multicast.py
Created by kueblc on 2019-01-25.
Encode data for Tuya smartconfig via multicast
multicast strategy reverse engineered by kueblc
"""

from crc import crc_32

from Cryptodome.Cipher import AES
pad = lambda data, block_size : data + ('\0' * ( (block_size - len(data)) % block_size ) )
aes = AES.new( b'a3c6794oiu876t54', AES.MODE_ECB )
encrypt = lambda data : aes.encrypt( pad(data, 16).encode() )

def encode_pw( pw ):
	r = []
	pw_bytes = [ ord(c) for c in pw ]
	encrypted_pw = encrypt(pw)
	# CRC and length are from plaintext
	crc = crc_32(pw_bytes)
	# length, twice
	r.append( len(pw) )
	r.append( len(pw) )
	# encode CRC as LE
	r.extend([ (crc >> i) & 255 for i in range(0,32,8) ])
	# payload, AES encrypted
	r.extend( encrypted_pw )
	return r

def encode_plain( s ):
	r = []
	s_bytes = [ ord(c) for c in s ]
	crc = crc_32(s_bytes)
	# length, twice
	r.append( len(s) )
	r.append( len(s) )
	# encode CRC as LE
	r.extend([ (crc >> i) & 255 for i in range(0,32,8) ])
	# payload, plaintext
	r.extend( s_bytes )
	return r

def bytes_to_ips( data, sequence ):
	r = []
	if len(data) & 1:
		data.append(0)
	for i in range(0, len(data), 2):
		r.append( "226." + str(sequence) + "." + str(data[i+1]) + "." + str(data[i]) )
		sequence += 1
	return r

multicast_head = bytes_to_ips([ ord(c) for c in "TYST01" ], 120)

def encode_multicast_body( password, ssid, token_group ):
	r = []
	ssid_encoded = encode_plain(ssid)
	r.extend( bytes_to_ips( ssid_encoded, 64 ) )
	password_encoded = encode_pw(password)
	r.extend( bytes_to_ips( password_encoded, 0 ) )
	token_group_encoded = encode_plain(token_group)
	r.extend( bytes_to_ips( token_group_encoded, 32 ) )
	return r

