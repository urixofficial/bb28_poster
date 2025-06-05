import pygame
from PySide6.QtWidgets import QWidget, QVBoxLayout, QLabel, QFileDialog
from PySide6.QtGui import QImage, QPixmap
from PySide6.QtCore import Qt, QSize
from modules.utils import hsv_to_rgb
from loguru import logger
import random
import numpy as np

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
        self.triangles = None
        self.triangle_brightness = {}  # Словарь для хранения яркости треугольников

        # Инициализация Pygame
        pygame.init()
        self.screen = pygame.Surface((self.frame_width, self.frame_height))
        self.screen.fill(self.rgb_bg_color)

        # Настройка PySide6 для отображения Pygame Surface
        self.canvas_widget = QLabel()
        self.canvas_layout = QVBoxLayout()
        self.canvas_layout.addWidget(self.canvas_widget)
        self.canvas.setLayout(self.canvas_layout)

    def render_frame(self, triangles):
        """Отрисовка кадра."""
        self.logger.debug("Отрисовка кадра")
        if not triangles:
            self.logger.warning("Получен пустой кадр")
            return
        self.triangles = triangles

        # Очистка словаря яркости при новом кадре, чтобы синхронизироваться с init_frame
        if not self.triangle_brightness:
            self.triangle_brightness.clear()

        # Очистка поверхности
        self.screen.fill(self.rgb_bg_color)

        # Отрисовка элементов
        if self.points_check:
            self.draw_points()
        if self.lines_check:
            self.draw_lines()
        if self.fill_check:
            self.draw_fill()

        # Преобразование Pygame Surface в QImage для отображения в PySide6
        pygame_image = pygame.image.tostring(self.screen, "RGB")
        qimage = QImage(pygame_image, self.frame_width, self.frame_height, QImage.Format.Format_RGB888)
        pixmap = QPixmap.fromImage(qimage)
        self.canvas_widget.setPixmap(pixmap.scaled(self.canvas_widget.size(), Qt.AspectRatioMode.KeepAspectRatio))

    def draw_points(self):
        """Отрисовка точек."""
        self.logger.debug(f"Отрисовка {len(self.triangles.points)} точек с размером {self.points_size}")
        for point in self.triangles.points:
            try:
                x, y = int(point[0]), int(point[1])
                pygame.draw.circle(self.screen, self.rgb_color, (x, y), self.points_size // 2)
            except (IndexError, TypeError) as e:
                self.logger.error(f"Ошибка при отрисовке точки {point}: {e}")

    def draw_lines(self):
        """Отрисовка линий."""
        self.logger.debug(f"Отрисовка линий с толщиной {self.lines_width}")
        if not self.triangles:
            self.logger.debug("Нет линий для отрисовки")
            return

        for simplex in self.triangles.simplices:
            try:
                # Получаем точки треугольника по индексам из simplex
                p1 = self.triangles.points[simplex[0]]
                p2 = self.triangles.points[simplex[1]]
                p3 = self.triangles.points[simplex[2]]

                # Отрисовка линий между вершинами треугольника
                pygame.draw.line(self.screen, self.rgb_color, (int(p1[0]), int(p1[1])), (int(p2[0]), int(p2[1])),
                                 self.lines_width)
                pygame.draw.line(self.screen, self.rgb_color, (int(p2[0]), int(p2[1])), (int(p3[0]), int(p3[1])),
                                 self.lines_width)
                pygame.draw.line(self.screen, self.rgb_color, (int(p3[0]), int(p3[1])), (int(p1[0]), int(p1[1])),
                                 self.lines_width)
            except (IndexError, TypeError) as e:
                self.logger.error(f"Ошибка при отрисовке треугольника {simplex}: {e}")

    def draw_fill(self):
        """Отрисовка заливки треугольников из триангуляции Делоне."""
        self.logger.debug("Отрисовка заливки")
        if not self.triangles:
            self.logger.debug("Нет треугольников для заливки")
            return

        for simplex in self.triangles.simplices:
            try:
                # Получаем точки треугольника
                p1 = self.triangles.points[simplex[0]]
                p2 = self.triangles.points[simplex[1]]
                p3 = self.triangles.points[simplex[2]]

                # Создаем ключ для треугольника на основе индексов вершин
                triangle_key = tuple(sorted(simplex))

                # Получаем яркость для треугольника
                if triangle_key not in self.triangle_brightness:
                    # Генерируем новую яркость с учетом разброса
                    base_brightness = self.hsv_color["v"]
                    variation = self.fill_variation
                    brightness = random.uniform(
                        max(0, base_brightness - variation),
                        min(100, base_brightness + variation)
                    )
                    self.triangle_brightness[triangle_key] = brightness
                else:
                    # Используем сохраненную яркость
                    brightness = self.triangle_brightness[triangle_key]

                # Преобразуем цвет с учетом оттенка основного цвета
                fill_color = hsv_to_rgb(
                    self.hsv_color["h"],
                    self.hsv_color["s"],
                    brightness
                )

                # Отрисовка треугольника
                pygame.draw.polygon(
                    self.screen,
                    fill_color,
                    [(int(p1[0]), int(p1[1])),
                     (int(p2[0]), int(p2[1])),
                     (int(p3[0]), int(p3[1]))]
                )
            except (IndexError, TypeError) as e:
                self.logger.error(f"Ошибка при заливке треугольника {simplex}: {e}")

    def save_image(self):
        """Сохранение изображения с использованием диалогового окна."""
        self.logger.debug("Открытие диалогового окна для сохранения изображения")
        try:
            # Открываем диалоговое окно для выбора пути сохранения
            file_dialog = QFileDialog(self.canvas)
            file_dialog.setAcceptMode(QFileDialog.AcceptMode.AcceptSave)
            file_dialog.setNameFilters(["PNG Image (*.png)", "JPEG Image (*.jpg *.jpeg)"])
            file_dialog.setDefaultSuffix("png")
            file_dialog.setWindowTitle("Сохранить кадр")

            if file_dialog.exec():
                file_path = file_dialog.selectedFiles()[0]
                self.logger.debug(f"Сохранение изображения в {file_path}")
                pygame.image.save(self.screen, file_path)
                self.logger.info(f"Изображение успешно сохранено в {file_path}")
            else:
                self.logger.debug("Сохранение изображения отменено")
        except Exception as e:
            self.logger.error(f"Ошибка при сохранении изображения: {e}")

    def set_points_check(self, flag):
        self.logger.debug(f"Установка флага отображения точек {flag}")
        self.points_check = flag
        self.render_frame(self.triangles)

    def set_points_size(self, value):
        self.logger.debug(f"Установка размера точек: {value}")
        self.points_size = value
        self.render_frame(self.triangles)

    def set_lines_check(self, flag):
        self.logger.debug(f"Установка флага отображения линий {flag}")
        self.lines_check = flag
        self.render_frame(self.triangles)

    def set_lines_width(self, value):
        self.logger.debug(f"Установка ширины линий: {value}")
        self.lines_width = value
        self.render_frame(self.triangles)

    def set_fill_check(self, flag):
        self.logger.debug(f"Установка флага отображения заливки {flag}")
        self.fill_check = flag
        self.render_frame(self.triangles)

    def set_fill_variation(self, value):
        self.logger.debug(f"Установка разброса яркости заливки: {value}")
        self.fill_variation = value
        # Перегенерируем яркость для всех треугольников при изменении разброса
        for triangle_key in self.triangle_brightness:
            base_brightness = self.hsv_color["v"]
            variation = self.fill_variation
            self.triangle_brightness[triangle_key] = random.uniform(
                max(0, base_brightness - variation),
                min(100, base_brightness + variation)
            )
        self.render_frame(self.triangles)

    def set_hue(self, value):
        self.logger.debug(f"Установка оттенка основного цвета: {value}")
        self.hsv_color["h"] = value
        self.rgb_color = hsv_to_rgb(self.hsv_color["h"], self.hsv_color["s"], self.hsv_color["v"])
        self.render_frame(self.triangles)

    def set_saturation(self, value):
        self.logger.debug(f"Установка насыщенности основного цвета: {value}")
        self.hsv_color["s"] = value
        self.rgb_color = hsv_to_rgb(self.hsv_color["h"], self.hsv_color["s"], self.hsv_color["v"])
        self.render_frame(self.triangles)

    def set_brightness(self, value):
        self.logger.debug(f"Установка яркости основного цвета: {value}")
        self.hsv_color["v"] = value
        self.rgb_color = hsv_to_rgb(self.hsv_color["h"], self.hsv_color["s"], self.hsv_color["v"])
        # Обновляем яркость треугольников с учетом нового базового значения
        for triangle_key in self.triangle_brightness:
            base_brightness = self.hsv_color["v"]
            variation = self.fill_variation
            self.triangle_brightness[triangle_key] = random.uniform(
                max(0, base_brightness - variation),
                min(100, base_brightness + variation)
            )
        self.render_frame(self.triangles)

    def set_bg_hue(self, value):
        self.logger.debug(f"Установка оттенка цвета фона: {value}")
        self.hsv_bg_color["h"] = value
        self.rgb_bg_color = hsv_to_rgb(self.hsv_bg_color["h"], self.hsv_bg_color["s"], self.hsv_bg_color["v"])
        self.render_frame(self.triangles)

    def set_bg_saturation(self, value):
        self.logger.debug(f"Установка насыщенности цвета фона: {value}")
        self.hsv_bg_color["s"] = value
        self.rgb_bg_color = hsv_to_rgb(self.hsv_bg_color["h"], self.hsv_bg_color["s"], self.hsv_bg_color["v"])
        self.render_frame(self.triangles)

    def set_bg_brightness(self, value):
        self.logger.debug(f"Установка яркости цвета фона: {value}")
        self.hsv_bg_color["v"] = value
        self.rgb_bg_color = hsv_to_rgb(self.hsv_bg_color["h"], self.hsv_bg_color["s"], self.hsv_bg_color["v"])
        self.render_frame(self.triangles)

    def set_color(self, h, s, v):
        self.logger.debug(f"Установка основного цвета: {h=} {s=} {v=}")
        self.hsv_color = {"h": h, "s": s, "v": v}
        self.rgb_color = hsv_to_rgb(h, s, v)
        # Обновляем яркость треугольников с учетом нового базового значения
        for triangle_key in self.triangle_brightness:
            base_brightness = self.hsv_color["v"]
            variation = self.fill_variation
            self.triangle_brightness[triangle_key] = random.uniform(
                max(0, base_brightness - variation),
                min(100, base_brightness + variation)
            )
        self.render_frame(self.triangles)

    def set_bg_color(self, h, s, v):
        self.logger.debug(f"Установка цвета фона: {h=} {s=} {v=}")
        self.hsv_bg_color = {"h": h, "s": s, "v": v}
        self.rgb_bg_color = hsv_to_rgb(h, s, v)
        self.render_frame(self.triangles)

    def __del__(self):
        """Очистка Pygame при уничтожении объекта."""
        pygame.quit()