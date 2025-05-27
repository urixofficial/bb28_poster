import random
import numpy as np
from loguru import logger
import sys

class AnimationManager:
    def __init__(self, config_manager, log_level="ERROR"):
        self.config = config_manager
        self.width = self.config.get_int("ImageParams", "default_width")
        self.height = self.config.get_int("ImageParams", "default_height")
        self.points_amount = self.config.get_int("GenerationParams", "points_amount_default")
        self.animation_speed = self.config.get_int("AnimationParams", "animation_speed_default")
        self.transition_speed = self.config.get_int("AnimationParams", "transition_speed_default")
        self.frame = None
        self.set_logger(log_level)

    @staticmethod
    def set_logger(log_level):
        logger.remove()
        logger.add(sys.stderr, format="{time} | {level} | {name}:{line} | {message}", level=log_level)

    def init_frame(self):
        logger.debug("Инициализация кадра")
        self.frame = {
            "points": np.array([[random.randint(0, self.width), random.randint(0, self.height)] for _ in range(self.points_amount)]),
            "lines": [],
            "fill": []
        }

    def get_frame(self):
        logger.debug("Отправка кадра")
        return self.frame

    def set_points_amount(self, value):
        logger.debug(f"Установка количества точек: {value}")
        self.points_amount = value
        self.init_frame()

    def set_width(self, value):
        logger.debug(f"Установка ширины: {value}")
        self.width = value
        self.init_frame()

    def set_height(self, value):
        logger.debug(f"Установка высоты: {value}")
        self.height = value
        self.init_frame()

    def set_animation_speed(self, value):
        logger.debug(f"Установка скорости анимации: {value}")
        self.animation_speed = value

    def set_transition_speed(self, value):
        logger.debug(f"Установка скорости переходов: {value}")
        self.transition_speed = value