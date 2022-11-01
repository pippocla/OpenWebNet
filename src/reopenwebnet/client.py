import asyncio
import logging
import socket

from reopenwebnet.protocol import OpenWebNetProtocol

_LOGGER = logging.getLogger(__name__)

class OpenWebNetClient:
    def __init__(self, host, port, password, session_type, name = "openwebnet"):
        self.host = host
        self.port = port
        self.password = password
        self.transport = None
        self.protocol = None
        self.on_con_lost = None
        self.session_type = session_type
        self.name = name

    async def start(self, event_callback=None):
        loop = asyncio.get_running_loop()
        mysock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        mysock.connect((self.host, self.port))
        on_con_lost = loop.create_future()
        on_session_start = loop.create_future()

        transport, protocol = await loop.create_connection(
            lambda: OpenWebNetProtocol(self.session_type, self.password, on_session_start, event_callback, on_con_lost, name=self.name),
            sock=mysock)

        await on_session_start
        self.transport = transport
        self.protocol = protocol
        self.on_con_lost = on_con_lost

    def send_message(self, msg):
        if self.protocol is None:
            _LOGGER.error("Could not send message; Did you call client.start()?")
            return
        self.protocol.send_message(msg)
