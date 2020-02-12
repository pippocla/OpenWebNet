# -*- coding: utf-8 -*-
import asyncio
from logging import getLogger

from reopenwebnet import messages
from reopenwebnet.protocol import OpenWebNetProtocol

_LOGGER = getLogger(__name__)


class CommandClient:

    def __init__(self, host, port, passwd):
        self.host = host
        self.port = port
        self.password = passwd

        self.shutdown = False
        self.transport = None
        self.buffer = ""
        self.message_buffer = []
        self.connect_timeout = 5
        self.reconnect_interval = 3600 * 24
        self.queue = None

    async def start(self):
        asyncio.ensure_future(self.connect_loop())

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
                lambda: OpenWebNetProtocol(messages.CMD_SESSION, self.password, self.on_connect,
                                           self.on_event, on_con_lost),
                self.host,
                self.port), self.connect_timeout)
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

    def on_connect(self):
        pass

    def on_event(self, msgs):
        asyncio.ensure_future(self.add_to_queue(msgs))

    async def add_to_queue(self, msgs):
        for msg in msgs:
            _LOGGER.debug("put message in queue: %s", msg)
            await self.queue.put(msg)

    async def send_command(self, message):
        while self.transport is None:
            _LOGGER.debug("not connected yet. waiting 1 second")
            await asyncio.sleep(1)

        self.queue = asyncio.Queue()
        _LOGGER.debug("sending message: %s", message)
        self.transport.write(str(message).encode('utf-8'))

        response = []
        while messages.ACK not in response and messages.NACK not in response:
            _LOGGER.debug("waiting for next message")
            msg = await self.queue.get()
            _LOGGER.debug("got message from queue: %s", msg)
            response.append(msg)

        return response

    def stop(self):
        self.shutdown = True
        if self.transport is not None:
            self.transport.close()
