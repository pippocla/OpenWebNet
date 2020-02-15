import os

import yaml
from yaml import SafeLoader


class Config:
    def __init__(self, host, port, password):
        self.host = host
        self.port = port
        self.password = password


def read_environment_config():
    default_config_path = os.path.expanduser('~/.reopenwebnet/config.yaml')
    config_path = os.environ.get('REOPENWEBNET_CONFIG', default_config_path)

    yml_config = yaml.load(open(config_path), Loader=SafeLoader)
    return Config(yml_config['host'], yml_config['port'], yml_config.get('password', None))
