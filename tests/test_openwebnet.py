#!/usr/bin/env python
# -*- coding: utf-8 -*-

import pytest
from openwebnet import OpenWebNet

__author__ = "Karel Vervaeke"
__copyright__ = "Karel Vervaeke"
__license__ = "mit"


def test_OpenWebNet_constructor():
    client = OpenWebNet('192.168.1.10', 20000, '123456')
    assert client._host == '192.168.1.10'
    assert client._port == 20000
    assert client._password == '123456'
