#!/usr/bin/env python3
# encoding: utf-8
"""
fake-registration-server.py
Created by nano on 2018-11-22.
Copyright (c) 2018 VTRUST. All rights reserved.
"""

import tornado.web
import tornado.locks
from tornado.options import define, options, parse_command_line

define("port", default=80, help="run on the given port", type=int)
define("addr", default="10.42.42.1", help="run on the given ip", type=str)
define("debug", default=True, help="run in debug mode")
define("secKey", default="0000000000000000", help="key used for encrypted communication")

import os
import signal

def exit_cleanly(signal, frame):
    print("Received SIGINT, exiting...")
    exit(0)

signal.signal(signal.SIGINT, exit_cleanly)

from Crypto.Cipher import AES
pad = lambda s: s + (16 - len(s) % 16) * chr(16 - len(s) % 16)
unpad = lambda s: s[:-ord(s[len(s) - 1:])]

from base64 import b64encode
import hashlib
import hmac
import binascii

import json
jsonstr = lambda j : json.dumps(j, separators=(',', ':'))

def file_as_bytes(file_name):
    with open(file_name, 'rb') as file:
        return file.read()

file_md5 = ""
file_sha256 = ""
file_hmac = ""
file_len = ""

def get_file_stats(file_name):
    #Calculate file hashes and size
    global file_md5
    global file_sha256
    global file_hmac
    global file_len
    file = file_as_bytes(file_name)
    file_md5 = hashlib.md5(file).hexdigest()
    file_sha256 = hashlib.sha256(file).hexdigest().upper()
    file_hmac = hmac.HMAC(options.secKey.encode(), file_sha256.encode(), 'sha256').hexdigest().upper()
    file_len = str(os.path.getsize(file_name))

from time import time
timestamp = lambda : int(time())

class FilesHandler(tornado.web.StaticFileHandler):
    def parse_url_path(self, url_path):
        if not url_path or url_path.endswith('/'):
            url_path = url_path + str('index.html')
        return url_path

class MainHandler(tornado.web.RequestHandler):
    def get(self):
        self.write("Hello, world")

class SchemaHandler(object):
    def __init__(self):
        self.notifier = tornado.locks.Condition()
        self.activated_ids = {}

    def get(self, gwId):
        # first try extended schema, otherwise minimal schema
        schema_key_count = 1 if gwId in self.activated_ids else 10
        # record that this gwId has been seen
        self.activated_ids[gwId] = True
        self.notifier.notify_all()
        return jsonstr([
            {"mode":"rw","property":{"type":"bool"},"id":1,"type":"obj"}] * schema_key_count)

schema = SchemaHandler()

class JSONHandler(tornado.web.RequestHandler):
    def get(self):
        self.post()
    def reply(self, result=None, encrypted=False):
        ts = timestamp()
        if encrypted:
            answer = {
                'result': result,
                't': ts,
                'success': True }
            answer = jsonstr(answer)
            payload = b64encode(AES.new(options.secKey, AES.MODE_ECB).encrypt(pad(answer))).decode()
            signature = "result=%s||t=%d||%s" % (payload, ts, options.secKey)
            signature = hashlib.md5(signature.encode()).hexdigest()[8:24]
            answer = {
                'result': payload,
                't': ts,
                'sign': signature }
        else:
            answer = {
                't': ts,
                'e': False,
                'success': True }
            if result:
                answer['result'] = result
        answer = jsonstr(answer)
        self.set_header("Content-Type", "application/json;charset=UTF-8")
        self.set_header('Content-Length', str(len(answer)))
        self.set_header('Content-Language', 'zh-CN')
        self.write(answer)
        print("reply", answer)
    def post(self):
        uri = str(self.request.uri)
        a = str(self.get_argument('a', 0))
        encrypted = str(self.get_argument('et', 0)) == '1'
        gwId = str(self.get_argument('gwId', 0))
        payload = self.request.body[5:]
        print()
        print(self.request.method, uri)
        print(self.request.headers)
        if payload:
            try:
                decrypted_payload = unpad(AES.new(options.secKey, AES.MODE_ECB).decrypt(binascii.unhexlify(payload))).decode()
                if decrypted_payload[0] != "{":
                    raise ValueError("payload is not JSON")
                print("payload", decrypted_payload)
            except:
                print("payload", payload.decode())

        if gwId == "0":
            print("WARNING: it appears this device does not use an ESP82xx and therefore cannot install ESP based firmware")

        # Activation endpoints
        if(a == "s.gw.token.get"):
            print("Answer s.gw.token.get")
            answer = {
                "gwApiUrl": "http://10.42.42.1/gw.json",
                "stdTimeZone": "-05:00",
                "mqttRanges": "",
                "timeZone": "-05:00",
                "httpsPSKUrl": "https://10.42.42.1/gw.json",
                "mediaMqttUrl": "10.42.42.1",
                "gwMqttUrl": "10.42.42.1",
                "dstIntervals": [] }
            if encrypted:
                answer["mqttsUrl"] = "10.42.42.1"
                answer["mqttsPSKUrl"] = "10.42.42.1"
                answer["mediaMqttsUrl"] = "10.42.42.1"
                answer["aispeech"] = "10.42.42.1"
            self.reply(answer)
            #os.system("killall smartconfig.js")

        elif(".active" in a):
            print("Answer s.gw.dev.pk.active")
            answer = {
                "schema": schema.get(gwId),
                "uid": "00000000000000000000",
                "devEtag": "0000000000",
                "secKey": options.secKey,
                "schemaId": "0000000000",
                "localKey": "0000000000000000" }
            self.reply(answer)
            print("TRIGGER UPGRADE IN 10 SECONDS")
            protocol = "2.2" if encrypted else "2.1"
            os.system("sleep 10 && ./mq_pub_15.py -i %s -p %s &" % (gwId, protocol))

        # Upgrade endpoints
        elif(".updatestatus" in a):
            print("Answer s.gw.upgrade.updatestatus")
            self.reply(None, encrypted)

        elif(".upgrade" in a) and encrypted:
            print("Answer s.gw.upgrade.get")
            answer = {
                "auto": 3,
                "size": file_len,
                "type": 0,
                "pskUrl": "http://10.42.42.1/files/upgrade.bin",
                "hmac": file_hmac,
                "version": "9.0.0" }
            self.reply(answer, encrypted)

        elif(".device.upgrade" in a):
            print("Answer tuya.device.upgrade.get")
            answer = {
                "auto": True,
                "type": 0,
                "size": file_len,
                "version": "9.0.0",
                "url": "http://10.42.42.1/files/upgrade.bin",
                "md5": file_md5 }
            self.reply(answer, encrypted)

        elif(".upgrade" in a):
            print("Answer s.gw.upgrade")
            answer = {
                "auto": 3,
                "fileSize": file_len,
                "etag": "0000000000",
                "version": "9.0.0",
                "url": "http://10.42.42.1/files/upgrade.bin",
                "md5": file_md5 }
            self.reply(answer, encrypted)

        # Misc endpoints
        elif(".log" in a):
            print("Answer atop.online.debug.log")
            answer = True
            self.reply(answer, encrypted)

        elif(".timer" in a):
            print("Answer s.gw.dev.timer.count")
            answer = {
                "devId": gwId,
                "count": 0,
                "lastFetchTime": 0 }
            self.reply(answer, encrypted)

        elif(".config.get" in a):
            print("Answer tuya.device.dynamic.config.get")
            answer = {
                "validTime": 1800,
                "time": timestamp(),
                "config": {} }
            self.reply(answer, encrypted)

        # Catchall
        else:
            print("Answer generic ({})".format(a))
            self.reply(None, encrypted)


def main():
    parse_command_line()
    get_file_stats('../files/upgrade.bin')
    app = tornado.web.Application(
        [
            (r"/", MainHandler),
            (r"/gw.json", JSONHandler),
            (r"/d.json", JSONHandler),
            ('/files/(.*)', FilesHandler, {'path': str('../files/')}),
        ],
        #template_path=os.path.join(os.path.dirname(__file__), "templates"),
        #static_path=os.path.join(os.path.dirname(__file__), "static"),
        debug=options.debug,
    )
    try:
        app.listen(options.port, options.addr)
        print("Listening on " + str(options.addr) + ":" + str(options.port))
        tornado.ioloop.IOLoop.current().start()
    except OSError as err:
        print("Could not start server on port " + str(options.port))
        if err.errno is 98: # EADDRINUSE
            print("Close the process on this port and try again")
        else:
            print(err)


if __name__ == "__main__":
    main()
