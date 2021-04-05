# -*- coding: utf-8 -*-
import asyncio
import socket
import struct
import time
from logging import getLogger

from reopenwebnet import messages
from reopenwebnet.password import calculate_password

_LOGGER = getLogger(__name__)


class OpenWebNetClient:
    def __init__(self, config, session_type, on_connect, on_event):
        self.config = config
        self.session_type = session_type
        self.on_connect = on_connect
        self.on_event = on_event

        self.reconnect_interval = 3600 * 24
        self.connect_timeout = 3

        self.shutdown = False
        self.transport = None

    async def start(self):
        await self.connect_loop()

    async def connect_loop(self):
        while not self.shutdown:
            try:
                # TODO: instead of fixed reconnect_interval schedule the reconnect at fixed moment of the day
                await asyncio.wait_for(self.connect(), self.reconnect_interval)
            except asyncio.TimeoutError:
                print("Was connected for %s seconds. Will reconnect" % self.reconnect_interval)

    async def connect(self):
        try:
            if self.transport is not None:
                self.transport.close()
                self.transport = None

            _LOGGER.debug("Trying to connect...")
            loop = asyncio.get_running_loop()
            on_con_lost = loop.create_future()
            transport, protocol = await asyncio.wait_for(loop.create_connection(
                lambda: OpenWebNetProtocol(self.session_type, self.config.password, self.on_connect,
                                           self.on_event, on_con_lost),
                self.config.host,
                self.config.port), self.connect_timeout)
            self.transport = transport

            await on_con_lost
            _LOGGER.debug("connection lost. will try again in 3 seconds")
            await asyncio.sleep(3)
        except KeyboardInterrupt:
            _LOGGER.debug("aborted by user")
            self.stop()

        except (asyncio.TimeoutError, OSError) as e:
            _LOGGER.debug("Failed to create connection in time. Will try again in 3 seconds")
            await asyncio.sleep(3)

    def stop(self):
        self.shutdown = True
        if self.transport is not None:
            self.transport.close()


class OpenWebNetProtocol(asyncio.Protocol):
    def __init__(self, session_type, password, connect_listener, event_listener, on_con_lost, write_delay=0.1):
        self.session_type = session_type
        self.on_con_lost = on_con_lost
        self.on_session_started = connect_listener
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
                if self.on_session_started is not None:
                    self.on_session_started()
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
