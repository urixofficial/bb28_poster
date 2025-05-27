import random
import numpy as np
from loguru import logger

class AnimationManager:
    def __init__(self, config_manager, log_level="ERROR"):
        numeric_log_level = logger.level(log_level).no if isinstance(log_level, str) else log_level
        self.logger = logger.bind(module_level=numeric_log_level)
        self.config = config_manager
        self.width = self.config.get_int("ImageParams", "width_default")
        self.height = self.config.get_int("ImageParams", "height_default")
        self.points_amount = self.config.get_int("GenerationParams", "points_amount_default")
        self.animation_speed = self.config.get_int("AnimationParams", "animation_speed_default")
        self.transition_speed = self.config.get_int("AnimationParams", "transition_speed_default")
        self.init_frame()

    def init_frame(self):
        self.logger.debug("Инициализация кадра")
        self.frame = {
            "points": np.array([[random.randint(0, self.width), random.randint(0, self.height)] for _ in range(self.points_amount)]),
            "lines": [],
            "fill": []
        }

    def get_frame(self):
        self.logger.debug("Чтение кадра")
        return self.frame

    def set_points_amount(self, value):
        self.logger.debug(f"Установка количества точек: {value}")
        self.points_amount = value
        self.init_frame()

    def set_width(self, value):
        self.logger.debug(f"Установка ширины: {value}")
        try:
            self.width = int(value)
            self.init_frame()
        except ValueError:
            self.logger.error(f"Некорректное значение ширины: {value}")

    def set_height(self, value):
        self.logger.debug(f"Установка высоты: {value}")
        try:
            self.height = int(value)
            self.init_frame()
        except ValueError:
            self.logger.error(f"Некорректное значение высоты: {value}")

    def set_animation_speed(self, value):
        self.logger.debug(f"Установка скорости анимации: {value}")
        self.animation_speed = value

    def set_transition_speed(self, value):
        self.logger.debug(f"Установка скорости переходов: {value}")
        self.transition_speed = value