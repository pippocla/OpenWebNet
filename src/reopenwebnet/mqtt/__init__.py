import asyncio
import logging
import re

import paho.mqtt.client as mqtt
from reopenwebnet import messages
from reopenwebnet.client import OpenWebNetClient

MQTT_LIGHT_COMMAND_PATTERN = re.compile('openwebnet/1/(\\d+)/cmd')

class MqttBridge:
    def __init__(self, config):
        if config.openwebnet is None:
            raise Exception('openwebnet configuration is required')

        if config.mqtt is None:
            raise Exception('mqtt configuration required')

        self.config = config

        self.event_client = OpenWebNetClient(config.openwebnet.host, config.openwebnet.port, config.openwebnet.password, messages.EVENT_SESSION, name="eventclient")
        self.mqtt = _create_mqtt_client(config.mqtt)

        self.mqtt.on_message = self.send_mqtt_command_to_openwebnet

    async def start(self):
        logging.debug('starting mqtt loop')
        self.mqtt.loop_start()

        logging.debug('starting event client')
        await self.event_client.start(self.send_openwebnet_event_to_mqtt)

    def send_mqtt_command_to_openwebnet(self, client, dummy, message):
        logging.debug('received mqtt message: %s / %s', message.topic, message.payload)
        match = MQTT_LIGHT_COMMAND_PATTERN.match(message.topic)
        if match is not None:
            what = message.payload.decode('ASCII')
            where = match.group(1)
            try:
                openwebnet_message = messages.NormalMessage(1, what, where)
                asyncio.run(self.send_openwebnet_message(openwebnet_message))
            except Exception as ex:
                logging.error("Failed to send message", ex)

    async def send_openwebnet_message(self, message):
        command_client = OpenWebNetClient(self.config.openwebnet.host, self.config.openwebnet.port,
                                          self.config.openwebnet.password, messages.CMD_SESSION,
                                          name="commandclient")
        await command_client.start(self.send_openwebnet_event_to_mqtt)
        command_client.send_message(message)
        command_client.transport.close()

    def send_openwebnet_event_to_mqtt(self, msgs):
        logging.debug('openwebnet messages received %s', msgs)
        for msg in msgs:
            # TODO: handle other 'who' types, allow registering transformations (to allow configuring different topic and payload)
            if isinstance(msg, messages.NormalMessage):
                if msg.who == '1':
                    topic = f"openwebnet/{msg.who}/{msg.where}/state"
                    logging.debug('publishing to %s: %s'%(topic, msg))
                    self.mqtt.publish(topic, msg.what)


def _create_mqtt_client(mqtt_config):
    client = mqtt.Client(mqtt_config.client_id)
    if mqtt_config.user is not None and mqtt_config.user != '':
        client.username_pw_set(mqtt_config.user, mqtt_config.password)

    def on_connect(client, b, c, d):
        logging.debug('mqtt connected %s/%s/%s/%s', client, b, c, d)
        client.subscribe('openwebnet/1/+/cmd')

    client.on_connect = on_connect
    client.connect(mqtt_config.host, port=mqtt_config.port)
    return client
