
import os
import yaml
from time import sleep
from client import get_command_client
import timeit

LIGHT = '17'

def main():
    client = get_command_client()

    print("Will indefinitely print light status with 1 second intervals")
    print("Try switching between networks & it should print 'None' while not connected to the right network, and resume normal operation when connected to the right network")

    while True:
        print(client.request_state('1', LIGHT))
        time.sleep(1)

if __name__ == '__main__':
    main()
