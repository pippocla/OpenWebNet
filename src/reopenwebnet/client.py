import asyncio
import socket

from reopenwebnet.protocol import OpenWebNetProtocol


class OpenWebNetClient:
    def __init__(self, host, port, password, session_type):
        self.host = host
        self.port = port
        self.password = password
        self.transport = None
        self.protocol = None
        self.on_con_lost = None
        self.session_type = session_type

    async def start(self, event_callback=None):
        loop = asyncio.get_running_loop()
        mysock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        mysock.connect((self.host, self.port))
        on_con_lost = loop.create_future()
        on_session_start = loop.create_future()

        transport, protocol = await loop.create_connection(
            lambda: OpenWebNetProtocol(self.session_type, self.password, on_session_start, event_callback, on_con_lost),
            sock=mysock)

        await on_session_start
        self.transport = transport
        self.protocol = protocol
        self.on_con_lost = on_con_lost

    def send_message(self, msg):
        self.protocol.send_message(msg)
