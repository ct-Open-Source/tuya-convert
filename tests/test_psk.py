#!/usr/bin/env python3
"""Test the smarthack.pskproxy module."""

# Copyright (c) 2020 Faidon Liambotis
# SPDX-License-Identifier: MIT

import pytest  # type: ignore

from smarthack.pskproxy import IDENTITY_PREFIX, gen_psk


PREFIX = b"\x01" + IDENTITY_PREFIX
HINT = b"1dHRsc2NjbHltbGx3eWh5" b"0000000000000000"  # taken from the code being tested
PRECOMPUTED = (
    ("", "310ab75a8d067ccea734482eb07adf04"),
    ("00" * 16, "3100cad5df5a8f719407b55e0ff55e883c53ab665efe02bd1bb93d7eda9e15e2"),
    ("80" * 16, "36ac9fe6f25bb46b652eeb78c9dbf2c6675f82bf574808da316295cab811efc5"),
    (
        "fef0f7f7d1fff1602f64cbdb482d86dc5f35949857a88ba085f9c17b7cae02ed95",
        "5578f55f9e82e8ab7ea053cbacc7a3f4cc1cfd51ac202a447c5e3155bf347078",
    ),
)


def test_gen_psk() -> None:
    """Test the gen_psk() method against precomputed data."""
    for clear, encrypted in PRECOMPUTED:
        identity = PREFIX + bytes.fromhex(clear)
        assert gen_psk(identity, HINT).hex() == encrypted

    with pytest.raises(ValueError):
        assert gen_psk(b"not 16 chars", HINT)
