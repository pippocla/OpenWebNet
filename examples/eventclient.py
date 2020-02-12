import asyncio
import logging

from reopenwebnet.client_factory import ClientFactory


async def eventclient_demo():
    def handle_connect():
        print("connected to openwebnet service")

    def handle_messages(msgs):
        print("received messages: ", msgs)

    client = ClientFactory().get_event_client(handle_connect, handle_messages)
    await client.start()

    print("Will listen for events for 1 hour. Hit ctrl-c to stop")
    await asyncio.sleep(3600)


if __name__ == '__main__':
    logging.basicConfig(level=logging.DEBUG)

    asyncio.run(eventclient_demo())
