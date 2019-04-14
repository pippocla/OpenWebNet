
import os
import yaml
from reopenwebnet import CommandClient, EventClient

def get_command_client():
    config = read_config()
    client = CommandClient(config['host'], config['port'], config['password'])

    return client

def get_event_client(connect_callback, message_callback):
    config = read_config()
    client = EventClient(config['host'], config['port'], config['password'], connect_callback, message_callback)

    return client

def read_config():
    if not os.path.exists('reopenwebnet_config.yml'):
        print("Please create a file named reopenwebnet_config.yml")
        print("See the sample file")

    config = yaml.load(open('reopenwebnet_config.yml'))
    return config

