#!/usr/bin/env python3
"""Test the smarthack.registration module."""

# Copyright (c) 2020 Faidon Liambotis
# SPDX-License-Identifier: MIT

import json
import os
from typing import Any

import pytest  # type: ignore

import tornado.httpclient
import tornado.web
from tornado.httpclient import AsyncHTTPClient, HTTPError
from tornado.httputil import url_concat

import smarthack.registration


# pylint: disable=bad-continuation


@pytest.fixture  # type: ignore
def app() -> tornado.web.Application:
    """Return the Tornado application that is about to be tested."""
    # this should be factored out in the registration module, and kept there
    return tornado.web.Application(
        [
            (r"/", smarthack.registration.MainHandler),
            (r"/gw.json", smarthack.registration.JSONHandler),
            ("/files/(.*)", smarthack.registration.FilesHandler, {"path": "files/"}),
            (r".*", tornado.web.RedirectHandler, {"url": "/", "permanent": False}),
        ],
    )


@pytest.mark.gen_test  # type: ignore
def test_file_status(tmp_path: Any) -> None:
    """Test the files/ hash generation method."""
    canary = tmp_path / "example"
    canary.write_text("example text")
    # hash for the text above
    hashes = {
        "len": "12",
        "md5": "f81e29ae988b19699abd92c59906d0ee",
        "sha256": "0E94AE36DA6FF03992A57FDDBDF4728B609D0D7FE6EB019FA9F1B9B5B540D835",
        "hmac": "2B449DB915DBD53F9DEC67A17CBB7583B73CA3939DB73DED1B6FB465C3E04DB7",
    }

    smarthack.registration.get_file_stats(canary)  # updates the globals, does not get
    for algorithm, precomputed in hashes.items():
        calculated = getattr(smarthack.registration, "file_%s" % algorithm)
        assert calculated == precomputed


@pytest.mark.gen_test  # type: ignore
async def test_main(http_client: AsyncHTTPClient, base_url: str) -> None:
    """Test the / endpoint."""
    response = await http_client.fetch(base_url)
    assert response.code == 200
    assert b"You are connected" in response.body


@pytest.mark.gen_test  # type: ignore
async def test_files(http_client: AsyncHTTPClient, base_url: str) -> None:
    """Test the /files endpoint."""
    with pytest.raises(HTTPError) as exc:
        await http_client.fetch(base_url + "/files", follow_redirects=False)
    assert "302" in str(exc.value)  # redirect


# These are real request data, grabbed from a Tuya firmware running a v3.0
# firmware on a third-party ESP8266 board (a Wemos D1 Mini)


@pytest.mark.gen_test  # type: ignore
async def test_gw_token_get(
    http_client: AsyncHTTPClient, base_url: str, monkeypatch: Any
) -> None:
    """Test the s.gw.token.get gw.json action."""
    # this (currently) calls os.system() with pkill -f, so avoid that
    monkeypatch.setattr(os, "system", lambda args: "")
    query_params = {
        "a": "s.gw.token.get",
        "et": "1",
        "gwId": "gwId=220388844c11ae0dd558",
        "other": json.dumps(
            {
                "token": "00000000",
                "region": "US",
                "tlinkStat": {
                    "configure": "smartconfig",
                    "time": 5,
                    "source": "ap",
                    "path": "broadcast",
                },
            },
            separators=(",", ":"),
        ),
        "t": "18",
        "v": "3.0",
        "sign": "a005aec554b96d565d0b0c6fa53cf1e5",
    }
    url = url_concat(base_url + "/gw.json", query_params)
    response = await http_client.fetch(url)
    assert response.code == 200


@pytest.mark.gen_test  # type: ignore
async def test_gw_dev_pk_active(
    http_client: AsyncHTTPClient, base_url: str, monkeypatch: Any
) -> None:
    """Test the s.gw.dev.pk.active gw.json action."""
    # this (currently) calls os.system() with mqtt.py, so avoid that
    monkeypatch.setattr(os, "system", lambda args: "")
    query_params = {
        "a": "s.gw.dev.pk.active",
        "et": "1",
        "gwId": "220388844c11ae0dd558",
        "other": '{"token":"00000000"}',
        "t": "18",
        "v": "3.0",
        "sign": "28c3d023f968d38774718d07134f681c",
    }
    request_body = "data=" + (
        "A097A0EEC194A5CFCBD8A4D45D20175C8F1EC6334F2A369082DDD7068AB0FDCD9094"
        + "4523C1D0202AB52DE65EB2E277B299AED0381C222325A4631633DA88CE2F4EAA0AB0"
        + "8C2850844E8E08CE1F2F69881D499B9BC25BF8531445272B7524FE76312ECE326346"
        + "AEA85F35C86FB54C22A9544398601077EEF61DE8AD3F7C53EB556717E2D8F22559FA"
        + "CC94165D2FEDBD826B7070B8204E3C1DBC3EFACC19415ABAA87562E4575DBD196E8B"
        + "9280E09E200EB8E7E5F74D7EE5CD415B1D3DB06423EB546768A05715059ECD33DBF3"
        + "48743E4D664232A62526E88F184F7F08947FF2222BE39822BFB7A4602F1E524CBA63"
        + "3F9AF83BB28712BB2979DB2D3BA53100DCD5BAFE65B03A14993DD1328D446DCCC70B"
    )
    url = url_concat(base_url + "/gw.json", query_params)
    response = await http_client.fetch(url, method="POST", body=request_body)
    assert response.code == 200


@pytest.mark.xfail(reason="encrypted payloads are (silently) ignored")  # type: ignore
@pytest.mark.gen_test  # type: ignore
async def test_dynamic_config_get(http_client: AsyncHTTPClient, base_url: str) -> None:
    """Test the tuya.device.dynamic.config.get gw.json action."""
    query_params = {
        "a": "tuya.device.dynamic.config.get",
        "et": "1",
        "gwId": "220388844c11ae0dd558",
        "t": "19",
        "v": "1.0",
        "sign": "72511d63bf1b8af30878e338d29967be",
    }
    request_body = "data=" + (
        "3195987275BE8BC18A834734649622440D005573E57F3F8EF41B1EC34DF14E3D3DB0"
        + "A807C4307FB91D1BD184C3D2B8C799ED2ACE9F43D57F1E7CA753DE937387BBEB0484"
        + "BE3F2AB8B28617AE7D3C2E61958A89BEC8FED97E4C9E09072727205A58838B0B407F"
        + "8A72421A483741E3932B"
    )
    url = url_concat(base_url + "/gw.json", query_params)
    response = await http_client.fetch(url, method="POST", body=request_body)
    assert response.code == 200


@pytest.mark.gen_test  # type: ignore
async def test_gw_update(http_client: AsyncHTTPClient, base_url: str) -> None:
    """Test the s.gw.update gw.json action."""
    query_params = {
        "a": "s.gw.update",
        "et": "1",
        "gwId": "220388844c11ae0dd558",
        "t": "1578488928",
        "v": "2.0",
        "sign": "73ffb8c3be0bfe18886a23c4af2aacfc",
    }
    request_body = "data=" + json.dumps(
        {
            "gwId": "220388844c11ae0dd558",
            "verSw": "3.1.2",
            "bv": "5.46",
            "pv": "2.2",
            "cdVer": "1.0.0",
            "devAttribute": 3,
        },
        separators=(",", ":"),
    )
    url = url_concat(base_url + "/gw.json", query_params)
    response = await http_client.fetch(url, method="POST", body=request_body)
    assert response.code == 200


@pytest.mark.gen_test  # type: ignore
async def test_gw_dev_update(http_client: AsyncHTTPClient, base_url: str) -> None:
    """Test the s.gw.dev.update gw.json action."""
    query_params = {
        "a": "s.gw.dev.update",
        "et": "1",
        "gwId": "220388844c11ae0dd558",
        "t": "1578488930",
        "v": "2.0",
        "sign": "f4547f0755874948c0b15dd8de7b2df8",
    }
    request_body = "data=" + json.dumps(
        {
            "devId": "220388844c11ae0dd558",
            "verSw": "1.0.0",
            "cdVer": "1.0.0",
            "devAttribute": 3,
        },
        separators=(",", ":"),
    )
    url = url_concat(base_url + "/gw.json", query_params)
    response = await http_client.fetch(url, method="POST", body=request_body)
    assert response.code == 200


@pytest.mark.gen_test  # type: ignore
async def test_atop_online_debug(http_client: AsyncHTTPClient, base_url: str) -> None:
    """Test the atop.online.debug.log gw.json action."""
    query_params = {
        "a": "atop.online.debug.log",
        "et": "1",
        "gwId": "220388844c11ae0dd558",
        "t": "1578488932",
        "sign": "cdb909a6475afdcf08e07fd0d7f9cbbf",
    }
    request_body = "data=" + json.dumps(
        {
            "data": 4,
            "exp": ", ".join(
                [
                    "epc1=0x00000000",
                    "epc2=0x00000000",
                    "epc3=0x00000000",
                    "excvaddr=0x00000000",
                    "depc=0x00000000",
                ]
            ),
        },
        separators=(",", ":"),
    )
    url = url_concat(base_url + "/gw.json", query_params)
    response = await http_client.fetch(url, method="POST", body=request_body)
    assert response.code == 200


@pytest.mark.gen_test  # type: ignore
@pytest.mark.parametrize("encrypted", (True, False))  # type: ignore
async def test_device_upgrade(
    http_client: AsyncHTTPClient, base_url: str, encrypted: bool
) -> None:
    """Test the tuya.device.upgrade.get gw.json action."""
    query_params = {
        "a": "tuya.device.upgrade.get",
        "et": "1" if encrypted else "0",
        "gwId": "220388844c11ae0dd558",
        "t": "1578488935",
        "v": "4.3",
        "sign": "be1b0b26925d66cae35e349d14a97436",
    }
    request_body = "data=" + '{"type":0}'
    url = url_concat(base_url + "/gw.json", query_params)
    response = await http_client.fetch(url, method="POST", body=request_body)
    assert response.code == 200


@pytest.mark.gen_test  # type: ignore
async def test_updatestatus(http_client: AsyncHTTPClient, base_url: str) -> None:
    """Test the s.gw.upgrade.updatestatus gw.json action."""
    query_params = {
        "a": "s.gw.upgrade.updatestatus",
        "et": "1",
        "gwId": "220388844c11ae0dd558",
        "t": "1578488935",
        "sign": "36fe90aaa82c9e1836a16ef40617b4d5",
    }
    request_body = "data=" + '{"upgradeStatus":2}'
    url = url_concat(base_url + "/gw.json", query_params)
    response = await http_client.fetch(url, method="POST", body=request_body)
    assert response.code == 200


# These are real request data, grabbed from unknown contributors on the web.
# They are reconstructed from logs, and as such, they may be inaccurate and/or
# partial.


@pytest.mark.gen_test  # type: ignore
async def test_gw_upgrade(http_client: AsyncHTTPClient, base_url: str) -> None:
    """Test the s.gw.upgrade gw.json action."""
    query_params = {
        "a": "s.gw.upgrade",
        "gwId": "01200950ecfabc795eb3",
        "t": "1523598924",
        "v": "2.0",
        "sign": "01468796fe75f6b66f2e5a8e67533349",
    }
    request_body = "data=" + '{"type":0}'  # unknown really
    url = url_concat(base_url + "/gw.json", query_params)
    response = await http_client.fetch(url, method="POST", body=request_body)
    assert response.code == 200


@pytest.mark.gen_test  # type: ignore
async def test_timer_count(http_client: AsyncHTTPClient, base_url: str) -> None:
    """Test the gw.dev.timer.count gw.json action."""
    query_params = {
        "a": "gw.dev.timer.count",
        "gwId": "01200950ecfabc795eb3",
        "t": "1523578939",
        "sign": "dc95e227bbd7bd6ca5036e1c68cd99f4",
    }
    request_body = ""
    url = url_concat(base_url + "/gw.json", query_params)
    response = await http_client.fetch(url, method="POST", body=request_body)
    assert response.code == 200
