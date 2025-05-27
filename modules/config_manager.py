import configparser
from loguru import logger

class ConfigManager:
    def __init__(self, config_path, log_level):
        numeric_log_level = logger.level(log_level).no if isinstance(log_level, str) else log_level
        self.logger = logger.bind(module_level=numeric_log_level)
        self.config = configparser.ConfigParser()
        self.config.read(config_path)

    def get_int(self, section, key):
        self.logger.debug(f"Чтение целого числа из конфигурации [{section}][{key}]")
        try:
            return self.config.getint(section, key)
        except (configparser.NoSectionError, configparser.NoOptionError) as e:
            self.logger.error(f"Ошибка чтения [{section}][{key}]: {e}")
            raise

    def get_str(self, section, key):
        self.logger.debug(f"Чтение строки из конфигурации [{section}][{key}]")
        try:
            return self.config.get(section, key)
        except (configparser.NoSectionError, configparser.NoOptionError) as e:
            self.logger.error(f"Ошибка чтения [{section}][{key}]: {e}")
            raise