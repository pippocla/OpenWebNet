# -*- coding: utf-8 -*-
import asyncore
import socket
from logging import getLogger

import threading

from reopenwebnet import messages
from reopenwebnet.password import calculate_password
from reopenwebnet.dispatcher import OpenWebNetEventDispatcher

_LOGGER = getLogger(__name__)


class EventClient:
    def __init__(self, host, port, password, connect_listener, event_listener):
        self.dispatcher = OpenWebNetEventDispatcher(host, int(port), self)
        self._password = password
        self.event_listener = event_listener
        self.connect_listener = connect_listener
        self._thread = threading.Thread(target=asyncore.loop, daemon=True)
        self.state = 'INITIAL'

    def start(self):
        self._thread.start()

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
