# -*- coding: utf-8 -*-
import asyncore
import socket
from logging import getLogger

from openwebnet import messages
from openwebnet.password import calculate_password

_LOGGER = getLogger(__name__)


class OpenWebNetEventDispatcher(asyncore.dispatcher):
    def __init__(self, host, port, event_listener):
        asyncore.dispatcher.__init__(self)
        self.create_socket(socket.AF_INET, socket.SOCK_STREAM)
        self.connect((host, port))
        self.buffer = ""
        self.read_buffer = ""
        self.event_listener = event_listener

    def handle_connect(self):
        _LOGGER.debug("connected", self)

    def handle_close(self):
        _LOGGER.debug("closed", self)

    def handle_read(self):
        read_result = self.recv(8196).decode()
        _LOGGER.debug("<---- %s", read_result)
        self.read_buffer += read_result
        if self.read_buffer[-2:] == "##":
            self.emit_messages()

    def emit_messages(self):
        message_list = messages.extract_messages(self.read_buffer)
        self.event_listener.handle_messages(message_list)
        self.read_buffer = ""

    def writable(self):
        return len(self.buffer) > 0

    def handle_write(self):
        sent = self.send(self.buffer.encode())
        _LOGGER.debug("----> %s", self.buffer[sent:])
        self.buffer = self.buffer[sent:]

    def write(self, data):
        self.buffer += data


class EventClient:
    def __init__(self, host, port, password, connect_listener, event_listener):
        self.dispatcher = OpenWebNetEventDispatcher(host, int(port), self)
        self._password = password
        self.event_listener = event_listener
        self.connect_listener = connect_listener

        self.state = 'INITIAL'

    def start(self):
        asyncore.loop()

    def handle_messages(self, msgs):
        _LOGGER.debug("%s - %s", self.state, msgs)

        if self.state == 'ERROR':
            _LOGGER.error("got messages in error state:", msgs)

        elif self.state == 'INITIAL':
            if msgs[-1] == messages.ACK:
                self.send_data(messages.EVENT_SESSION)
                self.state = 'EVENT_SESSION_REQUESTED'
            else:
                self.state = 'ERROR'
                raise asyncore.ExitNow('Server did not send ACK on connect')

        elif self.state == 'EVENT_SESSION_REQUESTED':
            if msgs[-1] == messages.NACK:
                self.state = 'ERROR'
            nonce = messages.extract_single(msgs[0])
            password = calculate_password(self._password, nonce)
            self.dispatcher.write(messages.generate_single(password))
            self.state = 'PASSWORD_SENT'

        elif self.state == 'PASSWORD_SENT':
            if msgs[-1] == messages.ACK:
                self.connect_listener()
                self.state = 'EVENT_SESSION_ACTIVE'
            else:
                raise asyncore.ExitNow('Server did not reply with ACK after sending password')
                self.state = 'ERROR'

        elif self.state == 'EVENT_SESSION_ACTIVE':
            self.event_listener(msgs)

    def send_data(self, data):
        self.dispatcher.write(data)
