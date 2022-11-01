# -*- coding: utf-8 -*-
import asyncio
import time
from logging import getLogger

from reopenwebnet import messages
from reopenwebnet.password import calculate_password

_LOGGER = getLogger(__name__)


class OpenWebNetProtocol(asyncio.Protocol):
    def __init__(self, session_type, password, on_session_start, event_listener, on_connection_lost,
                 name="opwenwebnet"):
        self.session_type = session_type
        self.password = password
        self.write_delay = 0.1
        self.on_session_start = on_session_start
        self.event_listener = event_listener
        self.on_connection_lost = on_connection_lost
        self.name = name

        self.state = 'NOT_CONNECTED'
        self.buffer = ""
        self.transport = None
        self.next_message = 0

    def connection_made(self, transport):
        self.state = 'CONNECTED'
        self.transport = transport

    def data_received(self, data):
        data = data.decode('utf-8')
        self.buffer += data

        msgs, remainder = messages.parse_messages(self.buffer)
        self.buffer = "" if remainder is None else remainder

        if self.state == 'ERROR':
            _LOGGER.error("got data in error state:", data)

        elif self.state == 'CONNECTED':
            if msgs[0] == messages.ACK:
                self._send_message(self.session_type)
                self.state = 'SESSION_REQUESTED'
            else:
                _LOGGER.error('Did not get initial ack on connect')
                self.state = 'ERROR'

        elif self.state == 'SESSION_REQUESTED':
            if msgs[-1] == messages.NACK:
                self.state = 'ERROR'
            nonce = msgs[0].value[2:-2]

            password = calculate_password(self.password, nonce)
            self._send_message(messages.FixedMessage(f"*#{password}##", messages.TYPE_OTHER))
            self.state = 'PASSWORD_SENT'

        elif self.state == 'PASSWORD_SENT':
            if msgs[-1] == messages.ACK:
                if self.on_session_start:
                    self.on_session_start.set_result(True)
                self.state = 'EVENT_SESSION_ACTIVE'
            else:
                _LOGGER.error('Failed to establish event session')
                self.state = 'ERROR'

        elif self.state == 'EVENT_SESSION_ACTIVE':
            _LOGGER.debug("sending messages to event listener %s", msgs)
            if self.event_listener is not None:
                self.event_listener(msgs)

    def _send_message(self, message):
        now = time.time()
        if now < self.next_message:
            time.sleep(self.next_message - now)
        self.next_message = now + self.write_delay
        self.transport.write(str(message).encode('utf-8'))

    def send_message(self, message):
        if self.state != 'EVENT_SESSION_ACTIVE':
            _LOGGER.error("Not sending message - session not active yet")
            # TODO: use an event to indicate when session is active
            return
        self._send_message(message)

    def connection_lost(self, exc):
        _LOGGER.debug("[%s] in protocol.connection_lost: %s", self.name, exc)
        self.state = 'NOT_CONNECTED'
        self.transport = None
        self.on_connection_lost.set_result(False)
