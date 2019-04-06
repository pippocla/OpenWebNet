
import os
import yaml
from time import sleep
from client import get_command_client

KITCHEN_LIGHT = '13'

def main():
    client = get_command_client()

    print_light_status(client, KITCHEN_LIGHT)
    sleep(3)

    turn_on(client, KITCHEN_LIGHT)
    print_light_status(client, KITCHEN_LIGHT)
    sleep(3)

    turn_off(client, KITCHEN_LIGHT)
    print_light_status(client, KITCHEN_LIGHT)

def turn_off(client, where):
    print("Sending light off command")
    client.light_off(where)

def turn_on(client, where):
    print("Sending light on command")
    client.light_on(where)

def print_light_status(client, where):
    status = client.light_status(where)

    if status:
        print("Light is currently on")
    else:
        print("Light is currently off")

if __name__ == '__main__':
    main()
