import configparser
from loguru import logger
import sys

class ConfigManager:
    def __init__(self, config_path, log_level):
        self.config = configparser.ConfigParser()
        self.config.read(config_path)
        self.set_logger(log_level)

    @staticmethod
    def set_logger(log_level):
        logger.remove()
        logger.add(sys.stderr, format="{time} | {level} | {name}:{line} | {message}", level=log_level)

    def get_int(self, section, key):
        logger.debug(f"Чтение целого числа из конфигурации [{section}][{key}]")
        return self.config.getint(section, key)

    def get_str(self, section, key):
        logger.debug(f"Чтение строки из конфигурации [{section}][{key}]")
        return self.config.get(section, key)