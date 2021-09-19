import asyncio
import logging

from reopenwebnet import messages
from reopenwebnet.client import OpenWebNetClient

logging.basicConfig(level=logging.DEBUG)


async def schedule_stop(delay):
    return asyncio.ensure_future(asyncio.sleep(delay))


async def main():
    def on_event(*args):
        print("got event", args)

    client = OpenWebNetClient('192.168.0.10', 20000, '951753', messages.CMD_SESSION)
    await client.start()

    # Play with the lights
    while True:
      await light_on(client)
      await asyncio.sleep(1)
      await light_off(client)
      await asyncio.sleep(40)



async def light_off(client):
    print("Light off")
    client.send_message(messages.NormalMessage(1, 0, 13))


async def light_on(client):
    print("Light on")
    client.send_message(messages.NormalMessage(1, 1, 13))


asyncio.run(main())
