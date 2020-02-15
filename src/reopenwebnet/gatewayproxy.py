import asyncio
import logging

from reopenwebnet import messages
from reopenwebnet.commandclient import CommandClient
from reopenwebnet.eventclient import EventClient
from reopenwebnet.messages import TYPE_NORMAL

LOGGER = logging.getLogger()


class GatewayProxy:
    def __init__(self, config, on_state_change=None):
        self.on_state_change = on_state_change

        def on_command_session():
            self.on_command_session()

        def on_event_session():
            self.on_event_session()

        def on_event(msgs):
            self.on_event(msgs)

        self.command_client = CommandClient(config, on_command_session)
        self.event_client = EventClient(config, on_event_session, on_event)

        self.states = {}

        self.listeners = {}

    def start(self):
        asyncio.ensure_future(self.command_client.start())
        asyncio.ensure_future(self.event_client.start())

    def register_listener(self, who, where, callback):
        self.listeners.setdefault(who, {})[where] = callback
        state = self.states.setdefault(who, {}).get(where, None)

        # send initial state
        if state is not None:
            callback(state)

    async def cmd(self, msg):
        return await self.command_client.send_command(msg)

    def on_command_session(self):
        asyncio.ensure_future(self.fetch_full_state())

    def on_event_session(self):
        asyncio.ensure_future(self.fetch_full_state())

    def on_event(self, msgs):
        self._process_messages(msgs)

    async def fetch_full_state(self):
        LOGGER.debug("fetching initial light states")
        initial_light_states = await self.send_cmd(messages.StatusRequestMessage('1', '0'))

        self._process_messages(initial_light_states)

    async def send_cmd(self, message):
        result = await self.command_client.send_command(message)
        return result

    def _process_messages(self, msgs):
        for msg in msgs:
            if msg.type == TYPE_NORMAL:
                item = self.states.setdefault(msg.who, {})
                current_value = item.get(msg.where, None)
                if current_value is None or current_value.what != msg.what:
                    if self.on_state_change is not None:
                        self.on_state_change(msg)
                    listener = self.listeners.get(msg.who, {}).get(msg.where, None)
                    if listener is not None:
                        listener(msg)
                self.states.setdefault(msg.who, {})[msg.where] = msg
