import asyncio
import logging
import re

import paho.mqtt.client as mqtt

from reopenwebnet import messages
from reopenwebnet.commandclient import CommandClient
from reopenwebnet.eventclient import EventClient

logging.basicConfig(level=logging.DEBUG)

MQTT_LIGHT_COMMAND_PATTERN = re.compile('/openwebnet/1/(\\d+)/cmd')


class MqttBridge:
    def __init__(self, config):
        if config.mqtt is None:
            raise Exception('mqtt configuration required')

        def on_command_session():
            logging.debug('openwebnet command session started')

        def on_event_session():
            logging.debug('openwebnet event session started')

        def on_event(msgs):
            logging.debug('openwebnet messages received %s', msgs)
            for msg in msgs:
                # TODO: handle other 'who' types, allow registering transformations (to allow configuring different topic and payload)
                if isinstance(msg, messages.NormalMessage):
                    if msg.who == '1':
                        self.mqtt.publish(f"/openwebnet/{msg.who}/{msg.where}/state", msg.what)

        self.command_client = CommandClient(config, on_command_session)
        self.event_client = EventClient(config, on_event_session, on_event)

        self.queue = asyncio.Queue()

        def on_mqtt_message(client, dummy, message):
            logging.debug('received mqtt message: %s / %s', message.topic, message.payload)
            match = MQTT_LIGHT_COMMAND_PATTERN.match(message.topic)
            if match is not None:
                payload = message.payload.decode('ASCII')

                async def send():
                    await self.command_client.send_command(messages.NormalMessage(1, payload, match.group(1)))

                asyncio.run(send())

        self.mqtt = _create_mqtt_client(config.mqtt)
        self.mqtt.on_message = on_mqtt_message

    async def start(self):
        logging.debug('starting mqtt bridge')
        self.mqtt.loop_start()
        await asyncio.wait([self.command_client.start(), self.event_client.start()])

def _create_mqtt_client(mqtt_config):
    client = mqtt.Client(mqtt_config.client_id)
    if mqtt_config.user is not None:
        client.username_pw_set(mqtt_config.user, mqtt_config.password)

    def on_connect(client, b, c, d):
        logging.debug('mqtt connected %s/%s/%s/%s', client, b, c, d)
        client.subscribe('/openwebnet/1/+/cmd')

    client.on_connect = on_connect
    client.connect(mqtt_config.host, port=mqtt_config.port)
    return client
