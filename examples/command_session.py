import asyncio
import logging

from reopenwebnet import messages
from reopenwebnet.client import OpenWebNetClient

logging.basicConfig(level=logging.DEBUG)

HOST = '192.168.0.10'
PORT = 20000
PASSWORD = '951753'
LIGHT_WHERE = 13


async def schedule_stop(delay):
    return asyncio.ensure_future(asyncio.sleep(delay))


async def main():
    def on_event(*args):
        print("got event", args)

    client = OpenWebNetClient(HOST, PORT, PASSWORD, messages.CMD_SESSION)
    await client.start()

    # Play with the lights
    for i in range(5):
        await light_on(client)
        await asyncio.sleep(1)
        await light_off(client)
        await asyncio.sleep(1)


async def light_off(client):
    print("Light off")
    client.send_message(messages.NormalMessage(1, 0, LIGHT_WHERE))


async def light_on(client):
    print("Light on")
    client.send_message(messages.NormalMessage(1, 1, LIGHT_WHERE))


asyncio.run(main())
