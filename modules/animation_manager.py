import random
import numpy as np
from loguru import logger

class AnimationManager:
    def __init__(self, config_manager, log_level="ERROR"):
        numeric_log_level = logger.level(log_level).no if isinstance(log_level, str) else log_level
        self.logger = logger.bind(module_level=numeric_log_level)
        self.config = config_manager
        self.frame_width = self.config.get_int("ImageParams", "width_default")
        self.frame_height = self.config.get_int("ImageParams", "height_default")
        self.fps = self.config.get_int("ImageParams", "fps_default")
        self.duration = self.config.get_int("ImageParams", "duration_default")
        self.points_amount = self.config.get_int("GenerationParams", "points_amount_default")
        self.animation_speed = self.config.get_int("AnimationParams", "animation_speed_default")
        self.transition_speed = self.config.get_int("AnimationParams", "transition_speed_default")
        self.init_frame()

    def init_frame(self):
        self.logger.debug("Инициализация кадра")
        self.frame = {
            "points": np.array([[random.randint(0, self.frame_width), random.randint(0, self.frame_height)] for _ in range(self.points_amount)]),
            "lines": [],
            "fill": []
        }

    def get_frame(self):
        self.logger.debug("Чтение кадра")
        return self.frame

    def set_points_amount(self, value):
        self.logger.debug(f"Установка количества точек: {value}")
        try:
            value = int(value)
            min_value = self.config.get_int("GenerationParams", "points_amount_min")
            max_value = self.config.get_int("GenerationParams", "points_amount_max")
            if not (min_value <= value <= max_value):
                raise ValueError(f"Количество точек быть в диапазоне [{min_value}, {max_value}]")
            self.points_amount = value
            self.init_frame()
        except (ValueError, TypeError) as e:
            self.logger.error(f"Некорректное количества точек: {value}, ошибка: {e}")

    def set_width(self, value):
        self.logger.debug(f"Установка ширины: {value}")
        try:
            value = int(value)
            min_value = self.config.get_int("ImageParams", "width_min")
            max_value = self.config.get_int("ImageParams", "width_max")
            if not (min_value <= value <= max_value):
                raise ValueError(f"Ширина должна быть в диапазоне [{min_value}, {max_value}]")
            self.frame_width = value
            self.init_frame()
        except (ValueError, TypeError) as e:
            self.logger.error(f"Некорректное значение ширины: {value}, ошибка: {e}")

    def set_height(self, value):
        self.logger.debug(f"Установка высоты: {value}")
        try:
            value = int(value)
            min_value = self.config.get_int("ImageParams", "height_min")
            max_value = self.config.get_int("ImageParams", "height_max")
            if not (min_value <= value <= max_value):
                raise ValueError(f"Высота должна быть в диапазоне [{min_value}, {max_value}]")
            self.frame_height = value
            self.init_frame()
        except (ValueError, TypeError) as e:
            self.logger.error(f"Некорректное значение высоты: {value}, ошибка: {e}")

    def set_fps(self, value):
        self.logger.debug(f"Установка частоты кадров: {value}")
        try:
            value = int(value)
            min_value = self.config.get_int("AnimationParams", "fps_min")
            max_value = self.config.get_int("AnimationParams", "fps_max")
            if not (min_value <= value <= max_value):
                raise ValueError(f"Частота кадров должна быть в диапазоне [{min_value}, {max_value}]")
            self.fps = value
            self.init_frame()
        except (ValueError, TypeError) as e:
            self.logger.error(f"Некорректное значение частоты кадров: {value}, ошибка: {e}")

    def set_duration(self, value):
        self.logger.debug(f"Установка длительности: {value}")
        try:
            value = int(value)
            min_value = self.config.get_int("AnimationParams", "duration_min")
            max_value = self.config.get_int("AnimationParams", "duration_max")
            if not (min_value <= value <= max_value):
                raise ValueError(f"Длительность должна быть в диапазоне [{min_value}, {max_value}]")
            self.duration = value
            self.init_frame()
        except (ValueError, TypeError) as e:
            self.logger.error(f"Некорректное значение длительности: {value}, ошибка: {e}")

    def set_animation_speed(self, value):
        self.logger.debug(f"Установка скорости анимации: {value}")
        try:
            value = int(value)
            min_value = self.config.get_int("AnimationParams", "animation_speed_min")
            max_value = self.config.get_int("AnimationParams", "animation_speed_max")
            if not (min_value <= value <= max_value):
                raise ValueError(f"Скорость анимации должна быть в диапазоне [{min_value}, {max_value}]")
            self.animation_speed = value
        except (ValueError, TypeError) as e:
            self.logger.error(f"Некорректное значение скорости анимации: {value}, ошибка: {e}")

    def set_transition_speed(self, value):
        self.logger.debug(f"Установка скорости переходов: {value}")
        try:
            value = int(value)
            min_value = self.config.get_int("AnimationParams", "transition_speed_min")
            max_value = self.config.get_int("AnimationParams", "transition_speed_max")
            if not (min_value <= value <= max_value):
                raise ValueError(f"Скорость переходов должна быть в диапазоне [{min_value}, {max_value}]")
            self.transition_speed = value
        except (ValueError, TypeError) as e:
            self.logger.error(f"Некорректное значение скорости переходов: {value}, ошибка: {e}")