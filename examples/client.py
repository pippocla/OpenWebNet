
import os
import yaml
from openwebnet import CommandClient, EventClient

def get_command_client():
    config = read_config()
    client = CommandClient(config['host'], config['port'], config['password'])

    return client

def get_event_client(connect_callback, message_callback):
    config = read_config()
    client = EventClient(config['host'], config['port'], config['password'], connect_callback, message_callback)

    return client

def read_config():
    if not os.path.exists('openwebnet_config.yml'):
        print("Please create a file named openwebnet_config.yml")
        print("See the sample file")

    config = yaml.load(open('openwebnet_config.yml'))
    return config

