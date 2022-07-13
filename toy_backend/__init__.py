import os
from config.config import Config
from config.logger import get_logger

config = Config(config_file='config.json')
logger = get_logger(logger_name='toy-backend', logging_config=config.logging)
logger.debug(config)