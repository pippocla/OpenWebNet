import os

import yaml
from yaml import SafeLoader


class Config:
    def __init__(self, config_dict):
        self.host = config_dict['host']
        self.port = config_dict.get('port', 20000)
        self.password = config_dict['password']

        self.mqtt = MqttConfig(config_dict['mqtt'])


class MqttConfig:
    def __init__(self, config_dict):
        self.host = config_dict['host']
        self.port = config_dict.get('port', 1883)
        self.user = config_dict.get('user')
        self.password = config_dict.get('password')
        self.client_id = config_dict.get('client_id')


def read_environment_config():
    default_config_path = os.path.expanduser('~/.reopenwebnet/config.yaml')
    config_path = os.environ.get('REOPENWEBNET_CONFIG', default_config_path)

    yml_config = yaml.load(open(config_path), Loader=SafeLoader)
    return Config(yml_config)
