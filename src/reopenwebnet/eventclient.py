# -*- coding: utf-8 -*-
import logging

from reopenwebnet import messages
from reopenwebnet.protocol import OpenWebNetClient

_LOGGER = logging.getLogger(__name__)


def main():
    logging.basicConfig(level=logging.DEBUG)


class EventClient:
    def __init__(self, config, on_session_start=None, event_listener=None):
        def on_event(msgs):
            if event_listener is not None:
                event_listener(msgs)
        self.client = OpenWebNetClient(config, messages.EVENT_SESSION, on_session_start, on_event)

    async def start(self):
        await self.client.start()

    def stop(self):
        self.client.stop()