# -*- coding: utf-8 -*-

from nose.tools import assert_equal
from reopenwebnet import messages
from reopenwebnet.messages import parse_message


def test_parse_messages_ack():
    assert_equal( parse_message(str(messages.ACK)), messages.ACK)


def test_parse_messages_nack():
    assert_equal( parse_message(str(messages.NACK)), messages.NACK)


def test_parse_messages_normal():
    actual = parse_message("*1*2*3##")

    assert_equal(actual.type, messages.TYPE_NORMAL)
    assert_equal(str(actual), '*1*2*3##')
    assert_equal(actual.who, '1')
    assert_equal(actual.what, '2')
    assert_equal(actual.where, '3')


def test_parse_messages_status_request():
    actual = parse_message("*#1*2##")

    assert_equal(actual.type, messages.TYPE_STATUS_REQUEST)
    assert_equal(str(actual), '*#1*2##')
    assert_equal(actual.who, '1')
    assert_equal(actual.where, '2')


def test_parse_messages_dimension_request():
    actual = parse_message("*#1*2*3##")

    assert_equal(actual.type, messages.TYPE_DIMENSION_REQUEST)
    assert_equal(str(actual), "*#1*2*3##")
    assert_equal(actual.who, '1')
    assert_equal(actual.where, '2')
    assert_equal(actual.dimension, '3')


def test_parse_messages_dimension_writing():
    actual = parse_message("*#1*2*#3*4*5##")

    assert_equal(actual.type, messages.TYPE_DIMENSION_WRITING)
    assert_equal(str(actual), "*#1*2*#3*4*5##")
    assert_equal(actual.who, '1')
    assert_equal(actual.where, '2')
    assert_equal(actual.dimension, '3')
    assert_equal(actual.values, ['4', '5'])

def test_parse_nonce_message():
    actual = parse_message("*#123456789##")

    assert_equal(actual.type, messages.TYPE_OTHER)
    assert_equal(actual.value, "*#123456789##")

