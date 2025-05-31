import pygame
from PySide6.QtWidgets import QWidget, QVBoxLayout, QLabel
from PySide6.QtGui import QImage, QPixmap
from PySide6.QtCore import Qt, QSize
from modules.utils import hsv_to_rgb
from loguru import logger


class RenderManager:
    def __init__(self, config_manager, canvas, log_level="INFO"):
        numeric_log_level = logger.level(log_level).no if isinstance(log_level, str) else log_level
        self.logger = logger.bind(module_level=numeric_log_level)
        self.logger.debug("Инициализация холста")

        self.config = config_manager
        self.canvas = canvas

        # Инициализация параметров из конфига
        self.points_check = self.config.get_bool("GenerationParams", "points_check")
        self.points_size = self.config.get_int("GenerationParams", "points_size_default")
        self.lines_check = self.config.get_bool("GenerationParams", "lines_check")
        self.lines_width = self.config.get_int("GenerationParams", "lines_width_default")
        self.fill_check = self.config.get_bool("GenerationParams", "fill_check")
        self.fill_variation = self.config.get_int("GenerationParams", "fill_variation_default")
        self.hsv_color = {
            "h": self.config.get_int("ColorParams", "hue_default"),
            "s": self.config.get_int("ColorParams", "saturation_default"),
            "v": self.config.get_int("ColorParams", "brightness_default")
        }
        self.hsv_bg_color = {
            "h": self.config.get_int("ColorParams", "bg_hue_default"),
            "s": self.config.get_int("ColorParams", "bg_saturation_default"),
            "v": self.config.get_int("ColorParams", "bg_brightness_default")
        }
        self.rgb_color = hsv_to_rgb(
            self.hsv_color["h"], self.hsv_color["s"], self.hsv_color["v"]
        )
        self.rgb_bg_color = hsv_to_rgb(
            self.hsv_bg_color["h"], self.hsv_bg_color["s"], self.hsv_bg_color["v"]
        )
        self.frame_width = self.config.get_int("ImageParams", "width_default")
        self.frame_height = self.config.get_int("ImageParams", "height_default")
        self.frame = None

        # Инициализация Pygame
        pygame.init()
        self.screen = pygame.Surface((self.frame_width, self.frame_height))
        self.screen.fill(self.rgb_bg_color)

        # Настройка PySide6 для отображения Pygame Surface
        self.canvas_widget = QLabel()
        self.canvas_layout = QVBoxLayout()
        self.canvas_layout.addWidget(self.canvas_widget)
        self.canvas.setLayout(self.canvas_layout)

    def render_frame(self, frame):
        """Отрисовка кадра."""
        self.logger.debug("Отрисовка кадра")
        if not frame:
            self.logger.warning("Получен пустой кадр")
            return
        self.frame = frame

        # Очистка поверхности
        self.screen.fill(self.rgb_bg_color)

        # Отрисовка элементов
        if self.points_check and "points" in self.frame:
            self.draw_points(self.frame["points"])
        if self.lines_check and "triangles" in self.frame:
            self.draw_lines(self.frame["triangles"])
        if self.fill_check and "triangles" in self.frame:
            self.draw_fill(self.frame["triangles"])

        # Преобразование Pygame Surface в QImage для отображения в PySide6
        pygame_image = pygame.image.tostring(self.screen, "RGB")
        qimage = QImage(pygame_image, self.frame_width, self.frame_height, QImage.Format.Format_RGB888)
        pixmap = QPixmap.fromImage(qimage)
        self.canvas_widget.setPixmap(pixmap.scaled(self.canvas_widget.size(), Qt.AspectRatioMode.KeepAspectRatio))

    def draw_points(self, points):
        """Отрисовка точек."""
        self.logger.debug(f"Отрисовка {len(points)} точек с размером {self.points_size}")
        for point in points:
            try:
                x, y = int(point[0]), int(point[1])
                pygame.draw.circle(self.screen, self.rgb_color, (x, y), self.points_size // 2)
            except (IndexError, TypeError) as e:
                self.logger.error(f"Ошибка при отрисовке точки {point}: {e}")

    def draw_lines(self, triangles):
        """Отрисовка линий."""
        self.logger.debug(f"Отрисовка линий с толщиной {self.lines_width}")
        if not triangles:
            self.logger.debug("Нет линий для отрисовки")
            return

        for simplex in triangles.simplices:
            try:
                # Получаем точки треугольника по индексам из simplex
                p1 = triangles.points[simplex[0]]
                p2 = triangles.points[simplex[1]]
                p3 = triangles.points[simplex[2]]

                # Отрисовка линий между вершинами треугольника
                pygame.draw.line(self.screen, self.rgb_color, (int(p1[0]), int(p1[1])), (int(p2[0]), int(p2[1])),
                                 self.lines_width)
                pygame.draw.line(self.screen, self.rgb_color, (int(p2[0]), int(p2[1])), (int(p3[0]), int(p3[1])),
                                 self.lines_width)
                pygame.draw.line(self.screen, self.rgb_color, (int(p3[0]), int(p3[1])), (int(p1[0]), int(p1[1])),
                                 self.lines_width)
            except (IndexError, TypeError) as e:
                self.logger.error(f"Ошибка при отрисовке треугольника {simplex}: {e}")

    def draw_fill(self, triangles):
        """Отрисовка заливки треугольников из триангуляции Делоне."""
        self.logger.debug("Отрисовка заливки")



    def save_image(self):
        """Сохранение изображения."""
        self.logger.debug("Сохранение изображения")
        pygame.image.save(self.screen, "frame.png")

    def set_points_check(self, flag):
        self.logger.debug(f"Установка флага отображения точек {flag}")
        self.points_check = flag
        self.render_frame(self.frame)

    def set_points_size(self, value):
        self.logger.debug(f"Установка размера точек: {value}")
        self.points_size = value
        self.render_frame(self.frame)

    def set_lines_check(self, flag):
        self.logger.debug(f"Установка флага отображения линий {flag}")
        self.lines_check = flag
        self.render_frame(self.frame)

    def set_lines_width(self, value):
        self.logger.debug(f"Установка ширины линий: {value}")
        self.lines_width = value
        self.render_frame(self.frame)

    def set_fill_check(self, flag):
        self.logger.debug(f"Установка флага отображения заливки {flag}")
        self.fill_check = flag
        self.render_frame(self.frame)

    def set_fill_variation(self, value):
        self.logger.debug(f"Установка разброса яркости заливки: {value}")
        self.fill_variation = value
        self.render_frame(self.frame)

    def set_hue(self, value):
        self.logger.debug(f"Установка оттенка основного цвета: {value}")
        self.hsv_color["h"] = value
        self.rgb_color = hsv_to_rgb(self.hsv_color["h"], self.hsv_color["s"], self.hsv_color["v"])
        self.render_frame(self.frame)

    def set_saturation(self, value):
        self.logger.debug(f"Установка насыщенности основного цвета: {value}")
        self.hsv_color["s"] = value
        self.rgb_color = hsv_to_rgb(self.hsv_color["h"], self.hsv_color["s"], self.hsv_color["v"])
        self.render_frame(self.frame)

    def set_brightness(self, value):
        self.logger.debug(f"Установка яркости основного цвета: {value}")
        self.hsv_color["v"] = value
        self.rgb_color = hsv_to_rgb(self.hsv_color["h"], self.hsv_color["s"], self.hsv_color["v"])
        self.render_frame(self.frame)

    def set_bg_hue(self, value):
        self.logger.debug(f"Установка оттенка цвета фона: {value}")
        self.hsv_bg_color["h"] = value
        self.rgb_bg_color = hsv_to_rgb(self.hsv_bg_color["h"], self.hsv_bg_color["s"], self.hsv_bg_color["v"])
        self.render_frame(self.frame)

    def set_bg_saturation(self, value):
        self.logger.debug(f"Установка насыщенности цвета фона: {value}")
        self.hsv_bg_color["s"] = value
        self.rgb_bg_color = hsv_to_rgb(self.hsv_bg_color["h"], self.hsv_bg_color["s"], self.hsv_bg_color["v"])
        self.render_frame(self.frame)

    def set_bg_brightness(self, value):
        self.logger.debug(f"Установка яркости цвета фона: {value}")
        self.hsv_bg_color["v"] = value
        self.rgb_bg_color = hsv_to_rgb(self.hsv_bg_color["h"], self.hsv_bg_color["s"], self.hsv_bg_color["v"])
        self.render_frame(self.frame)

    def set_color(self, h, s, v):
        self.logger.debug(f"Установка основного цвета: {h=} {s=} {v=}")
        self.hsv_color = {"h": h, "s": s, "v": v}
        self.rgb_color = hsv_to_rgb(h, s, v)
        self.render_frame(self.frame)

    def set_bg_color(self, h, s, v):
        self.logger.debug(f"Установка цвета фона: {h=} {s=} {v=}")
        self.hsv_bg_color = {"h": h, "s": s, "v": v}
        self.rgb_bg_color = hsv_to_rgb(h, s, v)
        self.render_frame(self.frame)

    def __del__(self):
        """Очистка Pygame при уничтожении объекта."""
        pygame.quit()