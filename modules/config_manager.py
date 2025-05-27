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
        log_format = ("<green>{time:YYYY-MM-DD HH:mm:ss}</green> | "
                      "<level>{level: <8}</level> | "
                      "<cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> | "
                      "<level>{message}</level>")
        logger.add(sys.stderr, format=log_format)

    def get_int(self, section, key):
        logger.debug(f"Чтение целого числа из конфигурации [{section}][{key}]")
        return self.config.getint(section, key)

    def get_str(self, section, key):
        logger.debug(f"Чтение строки из конфигурации [{section}][{key}]")
        return self.config.get(section, key)