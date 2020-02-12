# -*- coding: utf-8 -*-
import asyncio
import socket
import struct
import time
from logging import getLogger

from reopenwebnet import messages
from reopenwebnet.password import calculate_password

_LOGGER = getLogger(__name__)


class OpenWebNetProtocol(asyncio.Protocol):
    def __init__(self, session_type, password, connect_listener, event_listener, on_con_lost, write_delay=0.1):
        self.session_type = session_type
        self.on_con_lost = on_con_lost
        self.connect_listener = connect_listener
        self.event_listener = event_listener
        self.password = password
        self.write_delay = write_delay

        self.state = 'NOT_CONNECTED'
        self.buffer = ""
        self.transport = None
        self.next_message = 0

    def connection_made(self, transport):
        self.state = 'CONNECTED'
        self.transport = transport
        sock = transport.get_extra_info('socket')
        if sock is not None:
            sock.setsockopt(socket.SOL_SOCKET, socket.SO_SNDTIMEO, struct.pack('LL', 0, 10000))
            sock.setsockopt(socket.SOL_SOCKET, socket.SO_RCVTIMEO, struct.pack('LL', 0, 10000))

    def data_received(self, data):
        data = data.decode('utf-8')
        _LOGGER.debug("received data %s", data)
        self.buffer += data

        msgs, remainder = messages.parse_messages(self.buffer + data)
        self.buffer = "" if remainder is None else remainder

        if self.state == 'ERROR':
            _LOGGER.error("got data in error state:", data)

        elif self.state == 'CONNECTED':
            if msgs[0] == messages.ACK:
                self.send_message(self.session_type)
                self.state = 'SESSION_REQUESTED'
            else:
                _LOGGER.error('Did not get initial ack on connect')
                self.state = 'ERROR'

        elif self.state == 'SESSION_REQUESTED':
            if msgs[-1] == messages.NACK:
                self.state = 'ERROR'
            nonce = msgs[0].value[2:-2]

            password = calculate_password(self.password, nonce)
            self.send_message(messages.FixedMessage(f"*#{password}##", messages.TYPE_OTHER))
            self.state = 'PASSWORD_SENT'

        elif self.state == 'PASSWORD_SENT':
            if msgs[-1] == messages.ACK:
                self.state = 'EVENT_SESSION_ACTIVE'
                if self.connect_listener is not None:
                    self.connect_listener()
            else:
                _LOGGER.error('Failed to establish event session')
                self.state = 'ERROR'

        elif self.state == 'EVENT_SESSION_ACTIVE':
            _LOGGER.debug("sending messages to event listener %s", msgs)
            self.event_listener(msgs)

    def send_message(self, message):
        now = time.time()
        if now < self.next_message:
            time.sleep(self.next_message - now)
        self.next_message = now + self.write_delay
        self.transport.write(str(message).encode('utf-8'))

    def connection_lost(self, exc):
        self.state = 'NOT_CONNECTED'
        self.transport = None
        if not self.on_con_lost.done():
            self.on_con_lost.set_result(True)
