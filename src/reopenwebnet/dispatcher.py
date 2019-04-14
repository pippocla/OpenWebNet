# -*- coding: utf-8 -*-
import asyncore
import socket
from logging import getLogger

_LOGGER = getLogger(__name__)

from reopenwebnet import messages

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

