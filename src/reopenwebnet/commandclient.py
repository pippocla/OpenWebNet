# -*- coding: utf-8 -*-
import asyncio
from logging import getLogger
import logging

from reopenwebnet import messages
from reopenwebnet.protocol import OpenWebNetClient

_LOGGER = getLogger(__name__)

class CommandClient:
    def __init__(self, config, on_connect):
        self.on_connect = on_connect

        def on_session_started():
            if self.on_connect is not None:
                self.on_connect()

        self.client = OpenWebNetClient(config, messages.CMD_SESSION, on_session_started,
                                       lambda msgs: self.on_messages_received(msgs))

        self.read_queue = None
        self.lock = asyncio.Lock()

    async def start(self):
        logging.debug('command client starting')
        await self.client.start()

    def on_messages_received(self, msgs):
        # asyncio.ensure_future(self.add_to_queue(msgs))
        pass

    # async def add_to_queue(self, msgs):
    #     for msg in msgs:
    #         _LOGGER.debug('Adding to read queue: %s', msg)
    #         await self.read_queue.put(msg)

    async def send_command(self, message):
        async with self.lock:
            while self.client.transport is None:
                _LOGGER.debug("not connected yet. waiting 1 second")
                await asyncio.sleep(1)

            self.client.transport.write(str(message).encode('utf-8'))

            # self.read_queue = asyncio.Queue()
            # response = []
            # while messages.ACK not in response and messages.NACK not in response:
            #     _LOGGER.debug("waiting for next message")
            #     msg = await self.read_queue.get()
            #     _LOGGER.debug("got message from queue: %s", msg)
            #     response.append(msg)
            # print("RETURNING", response)
            return None

    def stop(self):
        self.client.stop()
