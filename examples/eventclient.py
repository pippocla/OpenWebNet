import asyncio
import logging

from reopenwebnet.config import read_environment_config
from reopenwebnet.eventclient import EventClient


async def eventclient_demo():
    def on_session_start():
        print("event session started")

    def on_event(msgs):
        print("received messages: ", msgs)

    client = EventClient(read_environment_config(), on_session_start, on_event)
    asyncio.ensure_future(client.start())

    print("Will listen for events for 1 hour. Hit ctrl-c to stop")
    await asyncio.sleep(3600)


if __name__ == '__main__':
    logging.basicConfig(level=logging.DEBUG)

    asyncio.run(eventclient_demo())
