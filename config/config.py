import json
import logging
import os

from config import CustomObject


class Config(CustomObject):
    LOGGING_LEVEL_MAP = {
        'error': logging.ERROR,
        'warning': logging.WARNING,
        'info': logging.INFO,
        'debug': logging.DEBUG,
    }

    def __init__(self, config_file):
        super(Config, self).__init__()
        if 'HOME' not in os.environ:
            raise RuntimeError('HOME not set')
        elif 'ENV' not in os.environ:
            raise RuntimeError('ENV not set')
        self.home = os.environ['HOME']
        self.env = os.environ['ENV']
        self.config_file = f'{self.home}/{config_file}'
        self.__load_config()

    def __load_config(self):
        # load JSON config
        with open(self.config_file) as config_file:
            config_loaded = json.load(config_file)
        default_config = config_loaded['production']

        # set testing config
        self.is_testing = not self.env.startswith('prod')
        if self.is_testing and 'testing' in config_loaded:
            self.__copy_config(default_config, config_loaded['testing'], overwrite=True)

        # dictionary to class attributes
        default_config['logging']['level'] = self.LOGGING_LEVEL_MAP[default_config['logging']['level']]
        self.__set_attrs(self, default_config)

    def __copy_config(self, dest_config, src_config, overwrite=False):
        for key, value in src_config.items():
            if not overwrite and key in dest_config:
                continue
            if type(value) == dict:
                if key not in dest_config:
                    dest_config[key] = {}
                self.__copy_config(dest_config[key], value, overwrite)
            else:
                dest_config[key] = value

    def __set_attrs(self, dest_cls, src_dict):
        for key, value in src_dict.items():
            if type(value) == dict:
                attr_cls = CustomObject()
                self.__set_attrs(attr_cls, src_dict[key])
                setattr(dest_cls, key, attr_cls)
            else:
                setattr(dest_cls, key, value)
