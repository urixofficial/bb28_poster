import random
import numpy as np
import triangle
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
        self.min_points_speed = self.config.get_int("AnimationParams", "min_points_speed_default")
        self.max_points_speed = self.config.get_int("AnimationParams", "max_points_speed_default")

        self.empty_areas = self.config.get_empty_areas()  # Получаем пустые области из конфига
        # Инициализация параметров движения для вершин пустых областей
        self.hole_vertex_params = self._init_hole_vertex_params()
        self.init_frame()

    def _init_hole_vertex_params(self):
        """Инициализация параметров движения для вершин пустых областей."""
        self.logger.debug("Инициализация параметров движения вершин пустых областей")
        params = []
        for area in self.empty_areas:
            area_params = []
            for vertex in area:
                # Случайный радиус движения (в пределах 10-50 пикселей)
                radius = np.random.uniform(10, 30)
                # Случайная угловая скорость (в радианах за кадр, от 0.01 до 0.05)
                angular_speed = np.random.uniform(0.01, 0.05)
                # Случайная начальная фаза (0-2π)
                phase = np.random.uniform(0, 2 * np.pi)
                area_params.append({
                    'center': np.array(vertex, dtype=np.float64),  # Центр вращения (исходная позиция)
                    'radius': radius,
                    'angular_speed': angular_speed,
                    'phase': phase,
                    'current_angle': phase  # Текущий угол для отслеживания
                })
            params.append(area_params)
        return params

    def init_frame(self):
        self.logger.debug("Инициализация кадра")

        # Генерация 4 статичных точек в углах
        corner_points = self._generate_corner_points()

        # Генерация 8 точек на сторонах (по 2 на каждую сторону)
        side_points = self._generate_side_points()

        # Генерация случайных точек внутри холста
        random_points = self._generate_random_points()

        # Объединяем все точки (угловые, боковые, случайные)
        points = np.concatenate([corner_points, side_points, random_points]).astype(np.float64)

        # Добавляем вершины пустых областей
        hole_points = []
        for area_params in self.hole_vertex_params:
            for param in area_params:
                # Начальная позиция вершины с учетом текущего угла
                center = param['center']
                radius = param['radius']
                angle = param['current_angle']
                x = center[0] + radius * np.cos(angle)
                y = center[1] + radius * np.sin(angle)
                hole_points.append([x, y])
        if hole_points:
            points = np.vstack([points, hole_points])

        # Генерация скоростей
        velocities = np.zeros((len(points), 2), dtype=np.float64)

        # Скорости для случайных точек (свободное движение)
        hole_vertices_count = sum(len(area) for area in self.empty_areas)
        for i in range(12, len(points) - hole_vertices_count):  # Начиная с индекса 12 до вершин пустых областей
            speed = np.random.uniform(self.min_points_speed, self.max_points_speed)
            angle = np.random.uniform(0, 2 * np.pi)
            velocities[i] = np.array([speed * np.cos(angle), speed * np.sin(angle)])

        # Скорости для точек на сторонах (движение только вдоль одной оси)
        for i in [4, 5, 6, 7]:
            velocities[i][0] = np.random.uniform(self.min_points_speed, self.max_points_speed) * np.random.choice([-1, 1])
            velocities[i][1] = 0  # Нет движения по Y
        for i in [8, 9, 10, 11]:
            velocities[i][0] = 0  # Нет движения по X
            velocities[i][1] = np.random.uniform(self.min_points_speed, self.max_points_speed) * np.random.choice([-1, 1])

        # Подготовка данных для триангуляции
        triangles = self._perform_triangulation(points)

        # Проверка, что все точки имеют связи
        if not self._verify_points_connectivity(points, triangles):
            self.logger.warning("Обнаружены точки без связей, повторная триангуляция")
            points, velocities = self._adjust_points_for_connectivity(points, velocities)
            triangles = self._perform_triangulation(points)

        self.frame = {
            "triangles": triangles,
            "velocities": velocities,
            "points": points
        }

    def _generate_corner_points(self):
        corner_points = np.array([
            [0, 0],  # Левый нижний угол
            [self.frame_width, 0],  # Правый нижний угол
            [0, self.frame_height],  # Левый верхний угол
            [self.frame_width, self.frame_height]  # Правый верхний угол
        ])
        return corner_points

    def _generate_side_points(self):
        """Генерация 8 точек на сторонах холста (по 2 на каждую сторону)."""
        side_points = []
        for _ in range(2):
            x = random.randint(0, self.frame_width)
            side_points.append([x, self.frame_height])
        for _ in range(2):
            x = random.randint(0, self.frame_width)
            side_points.append([x, 0])
        for _ in range(2):
            y = random.randint(0, self.frame_height)
            side_points.append([0, y])
        for _ in range(2):
            y = random.randint(0, self.frame_height)
            side_points.append([self.frame_width, y])
        return np.array(side_points)

    def _generate_random_points(self):
        """Генерация случайных точек, избегая пустых областей."""
        random_points = []
        for _ in range(self.points_amount):
            while True:
                point = [random.randint(0, self.frame_width), random.randint(0, self.frame_height)]
                if not self._is_point_in_holes(point):
                    random_points.append(point)
                    break
        return np.array(random_points)

    def _is_point_in_holes(self, point):
        """Проверка, находится ли точка внутри пустых областей."""
        for area_idx, area in enumerate(self.empty_areas):
            # Если frame существует (анимация), используем текущие позиции вершин
            if hasattr(self, 'frame') and 'points' in self.frame:
                current_area = []
                vertex_offset = len(self.frame["points"]) - sum(len(a) for a in self.empty_areas) + sum(
                    len(a) for a in self.empty_areas[:area_idx])
                for i in range(len(area)):
                    current_area.append(self.frame["points"][vertex_offset + i])
            else:
                # Во время инициализации используем статические координаты из empty_areas
                current_area = area
            if self._point_in_polygon(point, np.array(current_area)):
                return True
        return False

    def _point_in_polygon(self, point, polygon):
        """Проверка, находится ли точка внутри полигона (Ray Casting алгоритм)."""
        x, y = point
        n = len(polygon)
        inside = False
        j = n - 1
        for i in range(n):
            if ((polygon[i][1] > y) != (polygon[j][1] > y)) and \
               (x < (polygon[j][0] - polygon[i][0]) * (y - polygon[i][1]) /
                (polygon[j][1] - polygon[i][1]) + polygon[i][0]):
                inside = not inside
            j = i
        return inside

    def _perform_triangulation(self, points):
        """Выполнение триангуляции."""
        self.logger.debug("Выполняем триангуляцию с использованием triangle")
        try:
            tri_input = {
                'vertices': points,
            }
            boundary_segments = [
                [0, 1], [1, 3], [3, 2], [2, 0]  # Углы холста
            ]
            boundary_segments.extend([
                [4, 5],  # Верхняя сторона
                [6, 7],  # Нижняя сторона
                [8, 9],  # Левая сторона
                [10, 11]  # Правая сторона
            ])
            holes = []
            segments = boundary_segments
            vertex_offset = len(points) - sum(len(area) for area in self.empty_areas)
            if self.empty_areas:
                for area_idx, area in enumerate(self.empty_areas):
                    n_points = len(area)
                    for i in range(n_points):
                        segments.append([vertex_offset + i, vertex_offset + (i + 1) % n_points])
                    centroid = np.mean([self.frame["points"][vertex_offset + i] for i in range(n_points)], axis=0)
                    holes.append(centroid)
                    vertex_offset += n_points
                tri_input['holes'] = np.array(holes)
            tri_input['segments'] = np.array(segments)
            if len(points) >= 3:
                tri = triangle.triangulate(tri_input, 'p')
                return tri
            else:
                self.logger.warning("Недостаточно точек для триангуляции")
                return {'vertices': points, 'triangles': np.array([])}
        except Exception as e:
            self.logger.error(f"Ошибка при выполнении триангуляции: {e}")
            return {'vertices': points, 'triangles': np.array([])}

    def _verify_points_connectivity(self, points, triangles):
        """Проверка, что все точки участвуют в триангуляции."""
        if 'triangles' not in triangles or len(triangles['triangles']) == 0:
            return False
        used_vertices = set(triangles['triangles'].flatten())
        return all(i in used_vertices for i in range(len(points)))

    def _adjust_points_for_connectivity(self, points, velocities):
        self.logger.debug("Добавление точек для обеспечения связности")
        additional_points = []
        additional_velocities = []
        max_additional = max(0, self.points_amount + 12 - len(points))
        for _ in range(min(5, max_additional)):
            point = [random.randint(0, self.frame_width), random.randint(0, self.frame_height)]
            if not self._is_point_in_holes(point):
                additional_points.append(point)
                speed = np.random.uniform(self.min_points_speed, self.max_points_speed)
                angle = np.random.uniform(0, 2 * np.pi)
                additional_velocities.append([speed * np.cos(angle), speed * np.sin(angle)])
        if additional_points:
            points = np.vstack([points, additional_points])
            velocities = np.vstack([velocities, additional_velocities])
        return points, velocities

    def update_frame(self):
        self.logger.debug("Обновление кадра для анимации")
        self._update_points()
        self._update_hole_vertices()
        self._update_triangles()

    def _update_hole_vertices(self):
        """Обновление позиций вершин пустых областей по круговой траектории."""
        self.logger.debug("Обновление позиций вершин пустых областей")
        vertex_offset = len(self.frame["points"]) - sum(len(area) for area in self.empty_areas)
        for area_idx, area_params in enumerate(self.hole_vertex_params):
            for vertex_idx, param in enumerate(area_params):
                param['current_angle'] += param['angular_speed']
                center = param['center']
                radius = param['radius']
                angle = param['current_angle']
                x = center[0] + radius * np.cos(angle)
                y = center[1] + radius * np.sin(angle)
                point_idx = vertex_offset + sum(len(area) for area in self.empty_areas[:area_idx]) + vertex_idx
                self.frame["points"][point_idx] = [x, y]

    def _update_points(self):
        """Обновление положения точек с отталкиванием от пустых областей."""
        proposed_points = self.frame["points"].copy().astype(np.float64)
        hole_vertices_count = sum(len(area) for area in self.empty_areas)
        proposed_points[4:-hole_vertices_count] += self.frame["velocities"][4:-hole_vertices_count] * self.animation_speed

        for i in range(4, len(proposed_points) - hole_vertices_count):
            old_point = self.frame["points"][i]
            new_point = proposed_points[i]
            velocity = self.frame["velocities"][i]

            for area_idx, area in enumerate(self.empty_areas):
                current_area = []
                vertex_offset = len(self.frame["points"]) - sum(len(a) for a in self.empty_areas) + sum(len(a) for a in self.empty_areas[:area_idx])
                for j in range(len(area)):
                    current_area.append(self.frame["points"][vertex_offset + j])
                if self._point_in_polygon(new_point, np.array(current_area)):
                    closest_point = self._closest_point_on_polygon(old_point, np.array(current_area))
                    normal = self._compute_normal(old_point, closest_point)
                    self.frame["velocities"][i] = self._reflect_velocity(velocity, normal)
                    proposed_points[i] = old_point + self.frame["velocities"][i] * self.animation_speed

        self.frame["points"][4:-hole_vertices_count] = proposed_points[4:-hole_vertices_count].astype(np.float64)

        mask_x_low = self.frame["points"][4:-hole_vertices_count, 0] < 0
        mask_x_high = self.frame["points"][4:-hole_vertices_count, 0] > self.frame_width
        self.frame["points"][4:-hole_vertices_count][mask_x_low, 0] = -self.frame["points"][4:-hole_vertices_count][mask_x_low, 0]
        self.frame["velocities"][4:-hole_vertices_count][mask_x_low, 0] = -self.frame["velocities"][4:-hole_vertices_count][mask_x_low, 0]
        self.frame["points"][4:-hole_vertices_count][mask_x_high, 0] = 2 * self.frame_width - self.frame["points"][4:-hole_vertices_count][mask_x_high, 0]
        self.frame["velocities"][4:-hole_vertices_count][mask_x_high, 0] = -self.frame["velocities"][4:-hole_vertices_count][mask_x_high, 0]

        mask_y_low = self.frame["points"][4:-hole_vertices_count, 1] < 0
        mask_y_high = self.frame["points"][4:-hole_vertices_count, 1] > self.frame_height
        self.frame["points"][4:-hole_vertices_count][mask_y_low, 1] = -self.frame["points"][4:-hole_vertices_count][mask_y_low, 1]
        self.frame["velocities"][4:-hole_vertices_count][mask_y_low, 1] = -self.frame["velocities"][4:-hole_vertices_count][mask_y_low, 1]
        self.frame["points"][4:-hole_vertices_count][mask_y_high, 1] = 2 * self.frame_height - self.frame["points"][4:-hole_vertices_count][mask_y_high, 1]
        self.frame["velocities"][4:-hole_vertices_count][mask_y_high, 1] = -self.frame["velocities"][4:-hole_vertices_count][mask_y_high, 1]

        self.frame["points"][4:6, 1] = self.frame_height  # Верхняя сторона
        self.frame["points"][6:8, 1] = 0  # Нижняя сторона
        self.frame["points"][8:10, 0] = 0  # Левая сторона
        self.frame["points"][10:12, 0] = self.frame_width  # Правая сторона

    def _closest_point_on_polygon(self, point, polygon):
        min_dist = float('inf')
        closest_point = None
        n = len(polygon)
        for i in range(n):
            p1 = polygon[i]
            p2 = polygon[(i + 1) % n]
            cp = self._closest_point_on_segment(point, p1, p2)
            dist = np.linalg.norm(point - cp)
            if dist < min_dist:
                min_dist = dist
                closest_point = cp
        return closest_point

    def _closest_point_on_segment(self, point, p1, p2):
        p1 = np.array(p1)
        p2 = np.array(p2)
        point = np.array(point)
        segment = p2 - p1
        t = np.dot(point - p1, segment) / np.dot(segment, segment)
        t = max(0, min(1, t))
        projection = p1 + t * segment
        return projection

    def _compute_normal(self, point, boundary_point):
        normal = point - boundary_point
        norm = np.linalg.norm(normal)
        if norm > 0:
            normal /= norm
        else:
            normal = np.array([1, 0])
        return normal

    def _reflect_velocity(self, velocity, normal):
        v_dot_n = np.dot(velocity, normal)
        return velocity - 2 * v_dot_n * normal

    def _update_triangles(self):
        triangles = self._perform_triangulation(self.frame["points"])
        if not self._verify_points_connectivity(self.frame["points"], triangles):
            self.logger.warning("Обнаружены точки без связей, повторная триангуляция")
            points, velocities = self._adjust_points_for_connectivity(self.frame["points"], self.frame["velocities"])
            self.frame["points"] = points
            self.frame["velocities"] = velocities
            triangles = self._perform_triangulation(self.frame["points"])
        self.frame["triangles"] = triangles

    def get_frame(self):
        self.logger.debug("Получение кадра")
        return self.frame["triangles"]

    def set_points_amount(self, value):
        self.logger.debug(f"Установка количества точек: {value}")
        try:
            value = int(value)
            min_value = self.config.get_int("GenerationParams", "points_amount_min")
            max_value = self.config.get_int("GenerationParams", "points_amount_max")
            if not (min_value <= value <= max_value):
                raise ValueError(f"Количество точек должно быть в диапазоне [{min_value}, {max_value}]")
            self.points_amount = value
            self.init_frame()
        except (ValueError, TypeError) as e:
            self.logger.error(f"Некорректное количество точек: {value}, ошибка: {e}")

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
            min_value = self.config.get_int("ImageParams", "fps_min")
            max_value = self.config.get_int("ImageParams", "fps_max")
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
            min_value = self.config.get_int("ImageParams", "duration_min")
            max_value = self.config.get_int("ImageParams", "duration_max")
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

    def set_min_speed(self, value):
        self.logger.debug(f"Установка минимальной скорости: {value}")
        try:
            value = int(value)
            min_value = self.config.get_int("AnimationParams", "min_speed_min", 0)
            max_value = self.config.get_int("AnimationParams", "min_speed_max", self.max_points_speed)
            if not (min_value <= value <= max_value):
                raise ValueError(f"Минимальная скорость должна быть в диапазоне [{min_value}, {max_value}]")
            if value > self.max_points_speed:
                raise ValueError(f"Минимальная скорость не может превышать максимальную скорость ({self.max_points_speed})")
            self.min_points_speed = value
            self.init_frame()
        except (ValueError, TypeError) as e:
            self.logger.error(f"Некорректное значение минимальной скорости: {value}, ошибка: {e}")

    def set_max_speed(self, value):
        self.logger.debug(f"Установка максимальной скорости: {value}")
        try:
            value = int(value)
            min_value = self.config.get_int("AnimationParams", "max_speed_min", self.min_points_speed)
            max_value = self.config.get_int("AnimationParams", "max_speed_max", 10)
            if not (min_value <= value <= max_value):
                raise ValueError(f"Максимальная скорость должна быть в диапазоне [{min_value}, {max_value}]")
            if value < self.min_points_speed:
                raise ValueError(f"Максимальная скорость не может быть меньше минимальной скорости ({self.min_points_speed})")
            self.max_points_speed = value
            self.init_frame()
        except (ValueError, TypeError) as e:
            self.logger.error(f"Некорректное значение максимальной скорости: {value}, ошибка: {e}")