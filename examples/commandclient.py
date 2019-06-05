# @Author: michael
# @Date:   05-Jun-2019
# @Filename: commandclient.py
# @Last modified by:   michael
# @Last modified time: 05-Jun-2019
# @License: GNU GPL v3


import os
from time import sleep

import yaml

from client import get_command_client

KITCHEN_LIGHT = '13'

KITCHEN_SHUTTER = '52'


def main():
    client = get_command_client()

    print_status_all_lights(client)

    print_light_status(client, KITCHEN_LIGHT)
    sleep(3)

    turn_on(client, KITCHEN_LIGHT)
    print_light_status(client, KITCHEN_LIGHT)
    sleep(3)

    turn_off(client, KITCHEN_LIGHT)
    print_light_status(client, KITCHEN_LIGHT)
    sleep(3)

    turn_off_shutter(client, KITCHEN_SHUTTER)
    sleep(3)

    turn_on_shutter(client, KITCHEN_SHUTTER)


def print_status_all_lights(client):
    print("Fetching status of all lights with 1 command")
    print(client.request_state_multi('1', '0'))


def turn_off(client, where):
    print("Sending light off command")
    client.light_off(where)


def turn_on(client, where):
    print("Sending light on command")
    client.light_on(where)


def print_light_status(client, where):
    status = client.light_status(where)

    if status == '1':
        print("Light is currently on")
    elif status == '0':
        print("Light is currently off")
    else:
        print("Light status = ", status)


def turn_on_shutter(client, where):
    print("Sending shutter on command")
    client.shutter_on(where)


def turn_off_shutter(client, where):
    print("Sending shutter off command")
    client.shutter_off(where)


if __name__ == '__main__':
    main()
