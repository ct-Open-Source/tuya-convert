#!/usr/bin/env python3

import socket
import select
import ssl
import sslpsk

from Crypto.Cipher import AES
import hashlib
from binascii import hexlify, unhexlify

server_hint_hex = "316448527363324e6a62486c74624778336557683530303030303030303030303030303030" 
server_hint = unhexlify(server_hint_hex)


def listener(host, port):
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    sock.bind((host, port))
    sock.listen(1)
    return sock

def client(host, port):
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.connect((host, port))
    return sock
    

def get_psk(identity):
    id = identity
    server_hint = unhexlify(server_hint_hex)

    md5_uuid = id[17:(17+16)]
    source = id[1:50]

    rand = server_hint[21:21+16]

    key = hashlib.md5(rand).digest()
    to_encode = id[1:33]
    iv =  hashlib.md5(source).digest()
    cipher = AES.new(key ,AES.MODE_CBC, iv)

    c = cipher.encrypt(to_encode)
    print("PSK: %r"%(hexlify(c)))
    return c


class PskFrontend():
    def __init__(self, listening_host, listening_port, host, port):
        self.listening_port = listening_port
        self.listening_host = listening_host
        self.host = host
        self.port = port

        self.server_sock = listener(listening_host, listening_port)
        self.sessions = []
        self.hint = '1dHRsc2NjbHltbGx3eWh50000000000000000'



    def readables(self):
        readables = [self.server_sock]
        for (s1, s2) in self.sessions:
            readables.append(s1)
            readables.append(s2)
        return readables
    
    def new_client(self, s1):
        try:
            ssl_sock = sslpsk.wrap_socket(s1,
                server_side = True,
                ssl_version=ssl.PROTOCOL_TLSv1_2,
                ciphers='PSK-AES128-CBC-SHA256',
                psk=get_psk,
                hint=self.hint)

            s2 = client(self.host, self.port)
            self.sessions.append((ssl_sock, s2))
        except:
            pass
    def data_ready_cb(self, s):
        if s == self.server_sock:
            _s, frm = s.accept()
            print("new client on port %d from %r"%(self.listening_port, frm))
            self.new_client(_s)

        for (s1, s2) in self.sessions:
            if s == s1 or s == s2:
                c = s1 if s == s2 else s2
                try:
                    buf = s.recv(4096)
                    if len(buf) > 0:
                        c.send(buf)
                    else:
                        s1.shutdown(socket.SHUT_RDWR)
                        s2.shutdown(socket.SHUT_RDWR)
                        self.sessions.remove((s1,s2))
                except:
                    self.sessions.remove((s1,s2))
                    

def main():
    proxies = [PskFrontend('', 443, '127.0.0.1', 80), PskFrontend('', 8886, '127.0.0.1', 1883)]


    while True:
        readables = []
        for p in proxies:
            readables = readables + p.readables()
        r,_,_ =  select.select(readables, [], [])
        for s in r:
            for p in proxies:
                p.data_ready_cb(s)


if __name__ == '__main__':
    main()
