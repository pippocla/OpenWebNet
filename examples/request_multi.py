
import os
import yaml
import logging
from time import sleep
from client import get_command_client

logging.basicConfig(level=logging.DEBUG)

def main():
    client = get_command_client()

    print("Requesting all light states:")
    print(client.request_state_multi('1', '0'))

if __name__ == '__main__':
    main()
