import os
from config.config import Config
from config.logger import get_logger

config = Config(config_file='config.json')
logger = get_logger(logger_name='toy-logger', logging_config=config.logging)
parents_dir = os.path.join(config.output_basedir, __name__)
logger.info(config)