import asyncio
import logging

from reopenwebnet import messages
from reopenwebnet.client_factory import ClientFactory
from reopenwebnet.messages import TYPE_NORMAL

LOGGER = logging.getLogger()


class GatewayProxy:
    def __init__(self, event_listener=None):
        self.event_listener = event_listener

        self.states = {}
        self.command_client = None
        self.event_client = None

    async def start(self):
        def on_event_client_connect():
            asyncio.ensure_future(self.on_event_client_connect())

        def on_event(message):
            self._process_messages(message)

        factory = ClientFactory()
        self.command_client = factory.get_command_client()
        self.event_client = factory.get_event_client(on_event_client_connect, on_event)

        LOGGER.debug("starting command client")
        await self.command_client.start()

        LOGGER.debug("starting event client (async, so there is no 'start complete' log message)")
        await self.command_client.start()

        await self.fetch_all_light_states()

    async def on_event_client_connect(self):
        await self.fetch_all_light_states()

    async def fetch_all_light_states(self):
        LOGGER.debug("fetching initial light states")
        initial_light_states = await self.send_cmd(messages.StatusRequestMessage('1', '0'))

        self._process_messages(initial_light_states)

    async def send_cmd(self, message):
        result = await self.command_client.send_command(message)
        return result

    def print_states(self):
        for (who, state) in self.states.items():
            print("Who: ", who)
            for (k,v) in state.items():
                print(k, " --> ", v)

        print()

    def _process_messages(self, msgs):
        if self.event_listener is not None:
            self.event_listener(msgs)
        for msg in msgs:
            if msg.type == TYPE_NORMAL:
                self.states.setdefault(msg.who, {})[msg.where] = msg.what


async def gatewayproxy_demo():
    gw = GatewayProxy()

    await gw.start()
    print("Will print states every 3 seconds. Use Ctrl-C to stop")
    while True:
        await asyncio.sleep(3)
        gw.print_states()


if __name__ == "__main__":
    asyncio.run(gatewayproxy_demo())
