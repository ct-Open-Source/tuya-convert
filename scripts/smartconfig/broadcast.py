#!/usr/bin/env python3
# encoding: utf-8
"""
broadcast.py
Created by kueblc on 2019-01-25.
Encode data for Tuya smartconfig via broadcast
broadcast strategy ported from https://github.com/tuyapi/link
"""

from crc import crc_8

broadcast_head = [1, 3, 6, 10]


def encode_broadcast_body(password, ssid, token_group):
    r = []
    r.append(len(password))
    r.extend([ord(l) for l in password])
    r.append(len(token_group))
    r.extend([ord(l) for l in token_group])
    r.extend([ord(l) for l in ssid])
    e = []
    length = len(r)
    length_crc = crc_8([length])
    e.append(length >> 4 | 16)
    e.append(length & 0xF | 32)
    e.append(length_crc >> 4 | 48)
    e.append(length_crc & 0xF | 64)
    sequence = 0
    for i in range(0, length, 4):
        group = []
        group.append(sequence)
        group.extend(r[i : i + 4])
        group.extend([0] * (5 - len(group)))
        group_crc = crc_8(group)
        e.append(group_crc & 0x7F | 128)
        e.append(sequence | 128)
        e.extend([b | 256 for b in r[i : i + 4]])
        sequence += 1
    e.extend([256] * (length - i))
    return e
