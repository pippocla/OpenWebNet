# -*- coding: utf-8 -*-
import asyncio
import socket
import struct
from logging import getLogger

from reopenwebnet import messages
from reopenwebnet.protocol import OpenWebNetProtocol

_LOGGER = getLogger(__name__)


def main():
    logging.basicConfig(level=logging.DEBUG)


class EventClient:
    def __init__(self, host, port, password, connect_listener=None, event_listener=None):
        self.host = host
        self.port = port
        self.password = password
        self.connect_listener = connect_listener
        self.event_listener = event_listener

        self.shutdown = False
        self.transport = None
        self.connect_timeout = 5
        self.reconnect_interval = 3600 * 24

    async def start(self):
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

            print("Trying to connect...")
            loop = asyncio.get_running_loop()
            on_con_lost = loop.create_future()
            transport, protocol = await asyncio.wait_for(loop.create_connection(
                lambda: OpenWebNetProtocol(messages.EVENT_SESSION, self.password, self.connect_listener,
                                           self.event_listener, on_con_lost),
                self.host,
                self.port), self.connect_timeout)
            self.transport = transport
            await on_con_lost
            print("connection lost. will try again in 3 seconds")
            await asyncio.sleep(3)
        except KeyboardInterrupt:
            print("aborted by user")
            self.stop()
        except (asyncio.TimeoutError, OSError) as e:
            print("Failed to create connection in time. Will try again in 3 seconds")
            await asyncio.sleep(3)

    def stop(self):
        self.shutdown = True
        if self.transport is not None:
            self.transport.close()
            self.transport = None
