#!/usr/bin/env python3
# encoding: utf-8
"""
fake-registration-server.py
Created by nano on 2018-11-22.
Copyright (c) 2018 VTRUST. All rights reserved.
"""

import tornado.web
import os
import hashlib
import json
jsonstr = lambda j : json.dumps(j, separators=(',', ':'))

def file_as_bytes(file_name):
    with open(file_name, 'rb') as file:
        return file.read()

file_md5 = ""
file_len = ""

def get_file_stats(file_name):
    #Calculate MD5 and Filesize
    global file_md5
    global file_len
    file = file_as_bytes(file_name)
    file_md5 = hashlib.md5(file).hexdigest()
    file_len = str(os.path.getsize(file_name))

from time import time
timestamp = lambda : int(time())

from tornado.options import define, options, parse_command_line

define("port", default=80, help="run on the given port", type=int)
define("debug", default=True, help="run in debug mode")

class FilesHandler(tornado.web.StaticFileHandler):
    def parse_url_path(self, url_path):
        if not url_path or url_path.endswith('/'):
            url_path = url_path + str('index.html')
        return url_path

class MainHandler(tornado.web.RequestHandler):
    def get(self):
        self.write("Hello, world")

class JSONHandler(tornado.web.RequestHandler):
    def get(self):
        print('\n')
        print('URI:'+str(self.request.uri))
        self.write('Hello Human, Do you have IOT?')
    def reply(self, result=None):
        answer = {
            't': timestamp(),
            'e': False,
            'success': True }
        if result:
            answer['result'] = result
        answer = jsonstr(answer)
        self.set_header("Content-Type", "application/json;charset=UTF-8")
        self.set_header('Content-Length', str(len(answer)))
        self.set_header('Content-Language', 'zh-CN')
        self.write(answer)
    def post(self):
        print('\n')
        uri = str(self.request.uri)
        a = str(self.get_argument('a'))
        gwId = str(self.get_argument('gwId'))
        print('URI:'+uri)

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
            self.reply(answer)
            #os.system("killall smartconfig.js")

        elif(".active" in a):
            print("Answer s.gw.dev.pk.active")
            answer = {
                "schema": jsonstr([{
                    "mode": "rw",
                    "property": {
                        "type": "bool" },
                    "id": 1,
                    "type": "obj" }]),
                "uid": "00000000000000000000",
                "devEtag": "0000000000",
                "secKey": "0000000000000000",
                "schemaId": "0000000000",
                "localKey": "0000000000000000" }
            self.reply(answer)
            print("TRIGGER UPGRADE IN 10 SECONDS")
            os.system("./trigger_upgrade.sh %s &" % gwId)

        elif(".updatestatus" in a):
            print("Answer s.gw.upgrade.updatestatus")
            self.reply()

        elif(".device.upgrade" in a):
            print("Answer tuya.device.upgrade.get")
            answer = {
                "auto": True,
                "type": 0,
                "size": file_len,
                "version": "9.0.0",
                "url": "http://10.42.42.1/files/upgrade.bin",
                "md5": file_md5 }
            self.reply(answer)

        elif(".upgrade" in a):
            print("Answer s.gw.upgrade")
            answer = {
                "auto": 3,
                "fileSize": file_len,
                "etag": "0000000000",
                "version": "9.0.0",
                "url": "http://10.42.42.1/files/upgrade.bin",
                "md5": file_md5 }
            self.reply(answer)

        elif(".log" in a):
            print("Answer atop.online.debug.log")
            answer = True
            self.reply(answer)

        elif(".update" in a):
            print("Answer s.gw.update")
            self.reply()

        elif(".timer" in a):
            print("Answer s.gw.dev.timer.count")
            answer = {
                "devId": gwId,
                "count": 0,
                "lastFetchTime": 0 }
            self.reply(answer)

        elif(".config" in a):
            print("Answer tuya.device.dynamic.config.get")
            answer = {
                "validTime": 1800,
                "time": timestamp(),
                "config": {} }
            self.reply(answer)

        else:
            print("WARN: unknown request: {} ({})".format(a,uri))
            self.reply()


def main():
    parse_command_line()
    get_file_stats('../files/upgrade.bin')
    app = tornado.web.Application(
        [
            (r"/", MainHandler),
            (r"/gw.json", JSONHandler),
            ('/files/(.*)', FilesHandler, {'path': str('../files/')}),
        ],
        #template_path=os.path.join(os.path.dirname(__file__), "templates"),
        #static_path=os.path.join(os.path.dirname(__file__), "static"),
        debug=options.debug,
    )
    app.listen(options.port)
    print("Listening on port "+str(options.port))
    tornado.ioloop.IOLoop.current().start()


if __name__ == "__main__":
    main()
