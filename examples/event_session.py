import asyncio
from asyncio import FIRST_COMPLETED

from reopenwebnet.client import OpenWebNetClient
from reopenwebnet import messages

async def main():
    loop = asyncio.get_running_loop()

    # Start openwebnet protocol
    def on_event(*args):
        print("got event", args)

    client = OpenWebNetClient('192.168.0.10', 20000, '951753', session_type=messages.EVENT_SESSION)
    await client.start(on_event)

    # Schedule stop
    delay = 60
    print("Listening for openwebnet events for %d seconds. Try switching a light on and off" % delay)
    on_stop = asyncio.ensure_future(asyncio.sleep(delay))

    # Wait until scheduled stop or connection loss
    done, pending = await asyncio.wait([client.on_con_lost, on_stop], return_when=FIRST_COMPLETED)
    if client.on_con_lost in done:
        print("Connection lost")
    if on_stop in done:
        print("Scheduled stop")


asyncio.run(main())
