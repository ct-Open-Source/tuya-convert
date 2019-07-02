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
def file_as_bytes(file):
    with file:
        return file.read()

from tornado.options import define, options, parse_command_line

define("port", default=80, help="run on the given port", type=int)
define("addr", default="10.42.42.1", help="run on the given ip", type=str)
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
    def post(self):
        print('\n')
        uri = str(self.request.uri)
        a = str(self.get_argument('a'))
        print('URI:'+uri)
        
        if(a == "s.gw.token.get"):
            print("Answer s.gw.token.get")
            answer =(b'{"result":{"gwApiUrl":"http://10.42.42.1/gw.json","stdTimeZone":"-05:00","mqttRanges":"","timeZone":"-05:00",'
                     b'"httpsPSKUrl":"https://10.42.42.1/gw.json","mediaMqttUrl":"10.42.42.1","gwMqttUrl":"10.42.42.1","dstIntervals":[]},"t":7,"e":false,"success":true}\n'
                    )
            
            self.set_header("Content-Type", "application/json;charset=UTF-8")
            self.set_header('Content-Length', str(len(answer)))
            self.set_header('Content-Language', 'zh-CN')
            self.write(answer)
            #os.system("killall smartconfig.js")

        elif(".active" in a):
            print("Answer s.gw.dev.pk.active")
            index = uri.find("gwId=")+5
            gwId = uri[index:index+20]
            print("READ GW ID",gwId)
            answer =(b'{"result":'
                     b'{'
                       b'"schema":"[{'
                                    b'\\"mode\\":\\"rw\\",'
                                    b'\\"property\\":{\\"type\\":\\"bool\\"},\\"id\\":1,\\"type\\":\\"obj\\"'
                       b'}]",'
                       b'"uid":"00000000000000000000","devEtag":"0000000000","secKey":"0000000000000000","schemaId":"0000000000","localKey":"0000000000000000"'
                     b'},'
                     b'"t":7,"e":false,"success":true}\n'
                    )
            
            self.set_header("Content-Type", "application/json;charset=UTF-8")
            self.set_header('Content-Length', str(len(answer)))
            self.set_header('Content-Language', 'zh-CN')
            self.write(answer)
            print("TRIGGER UPGRADE IN 10 SECONDS")
            os.system("./trigger_upgrade.sh %s &" % str(gwId))

        elif(".upgrade" in a):
            print("Answer s.gw.upgrade")
            #Fixme
            #Calculate MD5 and Filesize
            file_md5 = hashlib.md5(file_as_bytes(open('../files/upgrade.bin', 'rb'))).hexdigest()
            file_len = os.path.getsize('../files/upgrade.bin')
            answer = b'{"result":{"auto":3,"fileSize":"%d","etag":"0000000000","version":"9.0.0","url":"http://10.42.42.1/files/upgrade.bin","md5":"%s"},"t":100,"e":false,"success":true}' % (file_len,file_md5.encode('utf-8'))
            print(answer)
            self.set_header("Content-Type", "application/json;charset=UTF-8")
            self.set_header('Content-Length', str(len(answer)))
            self.set_header('Content-Language', 'zh-CN')
            self.write(answer)

        elif(".debug.log" in a):
            print("Answer atop.online.debug.log")
            answer =b'{"result":true,"t":7,"e":false,"success":true}'
            self.set_header("Content-Type", "application/json;charset=UTF-8")
            self.set_header('Content-Length', str(len(answer)))
            self.set_header('Content-Language', 'zh-CN')
            self.write(answer)

        elif(".update" in a):
            print("Answer s.gw.update")
            answer =b'{"t":7,"e":false,"success":true}'
            self.set_header("Content-Type", "application/json;charset=UTF-8")
            self.set_header('Content-Length', str(len(answer)))
            self.set_header('Content-Language', 'zh-CN')
            self.write(answer)

        else:
            print("WARN: unknown request: {} ({})".format(a,uri))
            self.write("WARN: unknown request: "+uri)


def main():
    parse_command_line()
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
    try:
        app.listen(options.port, options.addr)
        print("Listening on " + str(options.addr) + ":" + str(options.port))
        tornado.ioloop.IOLoop.current().start()
    except OSError as err:
        print("Could not start server on port " + str(options.port))
        if err.errno is 98: # EADDRINUSE
            print("Close the process on this port and try again")


if __name__ == "__main__":
    main()
