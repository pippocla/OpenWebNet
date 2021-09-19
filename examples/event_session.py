import asyncio
import socket
from asyncio import FIRST_COMPLETED

from reopenwebnet import messages
from reopenwebnet.protocol import OpenWebNetProtocol

# logging.basicConfig(level=logging.DEBUG)

async def schedule_stop(delay):
    return asyncio.ensure_future(asyncio.sleep(delay))

async def main():
    loop = asyncio.get_running_loop()

    # Start openwebnet protocol
    def on_event(*args):
        print("got event", args)

    transport, protocol, on_con_lost = await start_openwebnet(loop, on_event)

    # Schedule stop
    delay = 10
    print("Listening for openwebnet events for %d seconds. Try switching a light on and off" % delay)
    on_stop = await schedule_stop(delay)

    # Wait until scheduled stop or connection loss
    done, pending = await asyncio.wait([on_con_lost, on_stop], return_when=FIRST_COMPLETED)
    if on_con_lost in done:
        print("Connection lost")
    if on_stop in done:
        print("Scheduled stop")


async def start_openwebnet(loop, on_event):
    mysock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    mysock.connect(('192.168.0.10', 20000))
    on_con_lost = loop.create_future()
    on_session_start = loop.create_future()

    transport, protocol = await loop.create_connection(
        lambda: OpenWebNetProtocol(messages.EVENT_SESSION, '951753', on_session_start, on_event, on_con_lost),
        sock=mysock)

    await on_session_start
    return transport, protocol, on_con_lost


asyncio.run(main())
