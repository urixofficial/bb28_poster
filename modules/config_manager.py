import configparser
from loguru import logger

class ConfigManager:
    def __init__(self, config_path, log_level):
        numeric_log_level = logger.level(log_level).no if isinstance(log_level, str) else log_level
        self.logger = logger.bind(module_level=numeric_log_level)
        self.config = configparser.ConfigParser()
        self.config.read(config_path)
        self.validate_config()

    def validate_config(self):
        self.logger.debug("Проверка конфигурации")
        for section in self.config.sections():
            for key, value in self.config.items(section):
                try:
                    if key.endswith('_min') or key.endswith('_max'):
                        int_value = self.config.getint(section, key)
                        if int_value < 0:
                            self.logger.error(f"Отрицательное значение в [{section}][{key}]: {value}")
                            raise ValueError(f"Отрицательное значение в [{section}][{key}]")
                except ValueError as e:
                    self.logger.error(f"Некорректное значение в [{section}][{key}]: {e}")
                    raise

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

    def get_bool(self, section, key):
        self.logger.debug(f"Чтение булевого значения из конфигурации [{section}][{key}]")
        try:
            return self.config.getboolean(section, key)
        except (configparser.NoSectionError, configparser.NoOptionError) as e:
            self.logger.error(f"Ошибка чтения [{section}][{key}]: {e}")
            raise