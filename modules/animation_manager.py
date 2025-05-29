import random
import numpy as np
from scipy.spatial import Delaunay
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

        # Генерация 4 статичных точек в углах
        corner_points = np.array([
            [0, 0],  # Левый нижний угол
            [self.frame_width, 0],  # Правый нижний угол
            [0, self.frame_height],  # Левый верхний угол
            [self.frame_width, self.frame_height]  # Правый верхний угол
        ])

        # Генерация случайных точек внутри холста
        random_points = np.array([
            [random.randint(0, self.frame_width), random.randint(0, self.frame_height)]
            for _ in range(self.points_amount)
        ])

        # Генерация 8 точек на сторонах (по 2 на каждую сторону)
        side_points = self._generate_side_points()

        # Объединяем все точки
        points = np.concatenate([corner_points, side_points, random_points])

        # Генерация скоростей
        max_speed = 5  # Максимальная скорость
        velocities = np.zeros((len(points), 2), dtype=np.int64)

        # Скорости для случайных точек (свободное движение)
        for i in range(4 + 8, len(points)):  # Начиная с индекса 12 (после угловых и боковых точек)
            velocities[i] = np.random.uniform(-max_speed, max_speed, 2).astype(np.int64)

        # Скорости для точек на сторонах (движение только вдоль одной оси)
        # Точки на верхней и нижней сторонах (индексы 4, 5, 6, 7) движутся по X
        for i in [4, 5, 6, 7]:
            velocities[i][0] = np.random.uniform(-max_speed, max_speed, 1).astype(np.int64)
            velocities[i][1] = 0  # Нет движения по Y
        # Точки на левой и правой сторонах (индексы 8, 9, 10, 11) движутся по Y
        for i in [8, 9, 10, 11]:
            velocities[i][0] = 0  # Нет движения по X
            velocities[i][1] = np.random.uniform(-max_speed, max_speed, 1).astype(np.int64)

        # Генерация линий с использованием триангуляции Делоне
        lines = []
        if len(points) >= 3:  # Для триангуляции нужно минимум 3 точки
            try:
                tri = Delaunay(points)
                for simplex in tri.simplices:
                    p1, p2, p3 = points[simplex]
                    lines.append([p1[0], p1[1], p2[0], p2[1]])  # p1 -> p2
                    lines.append([p2[0], p2[1], p3[0], p3[1]])  # p2 -> p3
                    lines.append([p3[0], p3[1], p1[0], p1[1]])  # p3 -> p1
            except Exception as e:
                self.logger.error(f"Ошибка при выполнении триангуляции: {e}")
        else:
            self.logger.warning("Недостаточно точек для триангуляции (требуется минимум 3 точки)")

        self.frame = {
            "points": points,
            "lines": lines,
            "fill": [],
            "velocities": velocities
        }

    def _generate_side_points(self):
        """Генерация 8 точек на сторонах холста (по 2 на каждую сторону)."""
        side_points = []
        # Верхняя сторона (y = frame_height)
        for _ in range(2):
            x = random.randint(0, self.frame_width)
            side_points.append([x, self.frame_height])
        # Нижняя сторона (y = 0)
        for _ in range(2):
            x = random.randint(0, self.frame_width)
            side_points.append([x, 0])
        # Левая сторона (x = 0)
        for _ in range(2):
            y = random.randint(0, self.frame_height)
            side_points.append([0, y])
        # Правая сторона (x = frame_width)
        for _ in range(2):
            y = random.randint(0, self.frame_height)
            side_points.append([self.frame_width, y])
        return np.array(side_points)

    def update_frame(self):
        self.logger.debug("Обновление кадра для анимации")
        # Обновляем позиции точек (кроме угловых)
        self.frame["points"][4:] += self.frame["velocities"][4:] * self.animation_speed

        # Ограничиваем точки рамками холста
        for i in range(4, len(self.frame["points"])):
            # Точки на верхней и нижней сторонах (индексы 4, 5, 6, 7)
            if i in [4, 5, 6, 7]:
                # Ограничение по X
                if self.frame["points"][i][0] < 0:
                    self.frame["points"][i][0] = -self.frame["points"][i][0]
                    self.frame["velocities"][i][0] = -self.frame["velocities"][i][0]
                elif self.frame["points"][i][0] > self.frame_width:
                    self.frame["points"][i][0] = 2 * self.frame_width - self.frame["points"][i][0]
                    self.frame["velocities"][i][0] = -self.frame["velocities"][i][0]
                # Фиксируем Y
                if i in [4, 5]:
                    self.frame["points"][i][1] = self.frame_height  # Верхняя сторона
                else:
                    self.frame["points"][i][1] = 0  # Нижняя сторона
            # Точки на левой и правой сторонах (индексы 8, 9, 10, 11)
            elif i in [8, 9, 10, 11]:
                # Ограничение по Y
                if self.frame["points"][i][1] < 0:
                    self.frame["points"][i][1] = -self.frame["points"][i][1]
                    self.frame["velocities"][i][1] = -self.frame["velocities"][i][1]
                elif self.frame["points"][i][1] > self.frame_height:
                    self.frame["points"][i][1] = 2 * self.frame_height - self.frame["points"][i][1]
                    self.frame["velocities"][i][1] = -self.frame["velocities"][i][1]
                # Фиксируем X
                if i in [8, 9]:
                    self.frame["points"][i][0] = 0  # Левая сторона
                else:
                    self.frame["points"][i][0] = self.frame_width  # Правая сторона
            # Остальные точки (свободное движение)
            else:
                if self.frame["points"][i][0] < 0:
                    self.frame["points"][i][0] = -self.frame["points"][i][0]
                    self.frame["velocities"][i][0] = -self.frame["velocities"][i][0]
                elif self.frame["points"][i][0] > self.frame_width:
                    self.frame["points"][i][0] = 2 * self.frame_width - self.frame["points"][i][0]
                    self.frame["velocities"][i][0] = -self.frame["velocities"][i][0]
                if self.frame["points"][i][1] < 0:
                    self.frame["points"][i][1] = -self.frame["points"][i][1]
                    self.frame["velocities"][i][1] = -self.frame["velocities"][i][1]
                elif self.frame["points"][i][1] > self.frame_height:
                    self.frame["points"][i][1] = 2 * self.frame_height - self.frame["points"][i][1]
                    self.frame["velocities"][i][1] = -self.frame["velocities"][i][1]

        # Пересчитываем линии с учетом новых позиций точек
        lines = []
        if len(self.frame["points"]) >= 3:
            try:
                tri = Delaunay(self.frame["points"])
                for simplex in tri.simplices:
                    p1, p2, p3 = self.frame["points"][simplex]
                    lines.append([p1[0], p1[1], p2[0], p2[1]])
                    lines.append([p2[0], p2[1], p3[0], p3[1]])
                    lines.append([p3[0], p3[1], p1[0], p1[1]])
            except Exception as e:
                self.logger.error(f"Ошибка при выполнении триангуляции: {e}")
        self.frame["lines"] = lines

    def get_frame(self):
        self.logger.debug("Получение кадра")
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