import os

import yaml
from yaml import SafeLoader

from reopenwebnet.commandclient import CommandClient
from reopenwebnet.eventclient import EventClient


class ClientFactory:
    def __init__(self):
        self.config_file = self.get_config_file()
        self.config = self.read_config()

    @staticmethod
    def get_config_file():
        env_path = os.environ.get('REOPENWEBNET_CONFIG', None)
        if env_path is not None:
            return env_path

        return os.path.expanduser('~/.reopenwebnet/config.yaml')

    def read_config(self):
        if not os.path.exists(self.config_file):
            print(f"Could not find config file at {self.config_file}")

        config = yaml.load(open(self.config_file), Loader=SafeLoader)
        return config

    def get_command_client(self):
        client = CommandClient(self.config['host'], self.config['port'], self.config['password'])

        return client

    def get_event_client(self, connect_callback, message_callback):
        client = EventClient(self.config['host'], self.config['port'], self.config['password'], connect_callback,
                             message_callback)

        return client
