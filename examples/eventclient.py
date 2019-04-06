
import os
import yaml
from time import sleep
from client import get_event_client

def main():
    client = get_event_client(handle_connect, handle_message)
    client.start()
    print("I will listen for events for 5 seconds. Try switching a few lights on and off")
    sleep(5)

def handle_connect():
    print("Connected with gateway")

def handle_message(msg):
    print(msg)

if __name__=='__main__':
    main()
