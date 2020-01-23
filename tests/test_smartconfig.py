#!/usr/bin/env python3
"""Test the smarthack.smartconfig module."""

# Copyright (c) 2020 Faidon Liambotis
# SPDX-License-Identifier: MIT

from smarthack.smartconfig import broadcast, multicast


def test_broadcast() -> None:
    """Test the SmartConfig broadcast message generation."""
    assert broadcast.broadcast_head == [1, 3, 6, 10]
    assert broadcast.encode_broadcast_body("password", "ssid", "token_group") == [
        17,
        41,
        48,
        65,
        247,
        128,
        264,
        368,
        353,
        371,
        254,
        129,
        371,
        375,
        367,
        370,
        245,
        130,
        356,
        267,
        372,
        367,
        198,
        131,
        363,
        357,
        366,
        351,
        172,
        132,
        359,
        370,
        367,
        373,
        235,
        133,
        368,
        371,
        371,
        361,
        130,
        134,
        356,
        256,
    ]


def test_multicast() -> None:
    """Test the SmartConfig multicast message generation."""
    assert multicast.multicast_head == [
        "226.120.89.84",
        "226.121.84.83",
        "226.122.49.48",
    ]
    assert multicast.encode_multicast_body("password", "ssid", "token_group") == [
        "226.64.4.4",
        "226.65.115.200",
        "226.66.240.153",
        "226.67.115.115",
        "226.68.100.105",
        "226.0.8.8",
        "226.1.70.213",
        "226.2.53.194",
        "226.3.125.46",
        "226.4.144.151",
        "226.5.255.33",
        "226.6.221.48",
        "226.7.209.44",
        "226.8.97.16",
        "226.9.220.184",
        "226.10.120.249",
        "226.32.11.11",
        "226.33.64.132",
        "226.34.206.30",
        "226.35.111.116",
        "226.36.101.107",
        "226.37.95.110",
        "226.38.114.103",
        "226.39.117.111",
        "226.40.0.112",
    ]
