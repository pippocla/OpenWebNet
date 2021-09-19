import asyncio
import logging
import socket

from reopenwebnet import messages
from reopenwebnet.protocol import OpenWebNetProtocol

logging.basicConfig(level=logging.DEBUG)


async def schedule_stop(delay):
    return asyncio.ensure_future(asyncio.sleep(delay))


async def main():
    loop = asyncio.get_running_loop()

    # Start openwebnet protocol
    def on_event(*args):
        print("got event", args)

    transport, protocol, on_con_lost = await start_openwebnet(loop, on_event)

    # Play with the lights
    await light_on(protocol)

    await asyncio.sleep(1)
    await light_off(protocol)

    await asyncio.sleep(1)
    await light_on(protocol)

    await asyncio.sleep(1)
    await light_off(protocol)


async def light_off(protocol):
    print("Light off")
    protocol.send_message(messages.NormalMessage(1, 0, 13))


async def light_on(protocol):
    print("Light on")
    protocol.send_message(messages.NormalMessage(1, 1, 13))


async def start_openwebnet(loop, on_event):
    mysock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    mysock.connect(('192.168.0.10', 20000))
    on_con_lost = loop.create_future()
    on_session_start = loop.create_future()

    transport, protocol = await loop.create_connection(
        lambda: OpenWebNetProtocol(messages.CMD_SESSION, '951753', on_session_start, on_event, on_con_lost),
        sock=mysock)

    await on_session_start
    return transport, protocol, on_con_lost


asyncio.run(main())
