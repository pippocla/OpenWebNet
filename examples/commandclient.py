import asyncio
from time import sleep

from reopenwebnet import messages

import logging

from reopenwebnet.commandclient import CommandClient
from reopenwebnet.config import read_environment_config

KITCHEN_LIGHT = '13'

logging.basicConfig(level=logging.INFO)


async def commandclient_demo():
    def on_connect():
        print("command session started")
    client = CommandClient(read_environment_config(), on_connect)

    asyncio.ensure_future(client.start())

    await example_single_light_status(client)
    await example_all_lights_status_request(client)
    await example_light_commands(client)


async def example_light_commands(client):
    print("2 x turn light on & turn it off again")
    for i in range(2):
        print("on")
        print(await client.send_command(messages.NormalMessage('1', '1', KITCHEN_LIGHT)))
        sleep(1)
        print("off")
        print(await client.send_command(messages.NormalMessage('1', '0', KITCHEN_LIGHT)))
        sleep(1)

    print("Requesting light status")
    print(await client.send_command(messages.StatusRequestMessage('1', KITCHEN_LIGHT)))
    sleep(1)


async def example_all_lights_status_request(client):
    print("Request all lights status")
    print(await client.send_command(messages.StatusRequestMessage('1', '0')))
    sleep(1)


async def example_single_light_status(client):
    print("3 x Request light status with 3 second intervals")
    for i in range(3):
        print(await client.send_command(messages.StatusRequestMessage('1', KITCHEN_LIGHT)))
        await asyncio.sleep(3)


def turn_on_shutter(client, where):
    print("Sending shutter on command")
    client.shutter_on(where)


def turn_off_shutter(client, where):
    print("Sending shutter off command")
    client.shutter_off(where)


if __name__ == '__main__':
    logging.basicConfig(level=logging.DEBUG)

    asyncio.run(commandclient_demo())
