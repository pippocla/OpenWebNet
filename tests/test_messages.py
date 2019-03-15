# -*- coding: utf-8 -*-

from openwebnet.messages import extract_messages
from openwebnet import messages


def test_extract_messages_nack():
    assert extract_messages(messages.NACK) == [messages.NACK]


def test_extract_messages_nack_nack():
    assert extract_messages(messages.NACK + messages.NACK) == [messages.NACK, messages.NACK]


def test_extract_messages_ack_ack():
    assert extract_messages(messages.ACK + messages.ACK) == [messages.ACK, messages.ACK]


def test_extract_value_and_ack():
    value_message = "*1#0#13##"
    assert extract_messages(value_message + messages.ACK) == [value_message, messages.ACK]