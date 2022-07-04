import os
import logging
from logging.handlers import TimedRotatingFileHandler


def get_logger(logger_name, logging_config):
    """
    Initialise a logger
    :return: None
    """
    logger = logging.getLogger(logger_name + '-logger')
    logging_format = logging.Formatter('%(asctime)s - %(levelname)s - [%(filename)s:%(lineno)d] %(message)s')
    logger.setLevel(logging_config.level)
    create_dir(logging_config.path)

    # leave log in a file
    file_log = TimedRotatingFileHandler(filename=f'{logging_config.path}/{logger_name}.log',
                                        when='midnight',
                                        interval=1,
                                        encoding='utf-8')
    file_log.suffix = '%Y%m%d'
    file_log.setFormatter(logging_format)
    logger.addHandler(file_log)

    # display log on the console
    console_log = logging.StreamHandler()
    console_log.setFormatter(logging_format)
    logger.addHandler(console_log)

    return logger


def create_dir(dir_name):
    if not os.path.isdir(dir_name):
        os.makedirs(dir_name)