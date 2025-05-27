from PySide6.QtOpenGLWidgets import QOpenGLWidget
from OpenGL.GL import *
import colorsys
from loguru import logger


class OpenGLCanvas(QOpenGLWidget):
	def __init__(self, config_manager, parent=None, log_level="INFO"):
		super().__init__(parent)
		numeric_log_level = logger.level(log_level).no if isinstance(log_level, str) else log_level
		self.logger = logger.bind(module_level=numeric_log_level)
		self.config = config_manager
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
		self.rgb_color = self.hsv_to_rgb(
			self.config.get_int("ColorParams", "hue_default"),
			self.config.get_int("ColorParams", "saturation_default"),
			self.config.get_int("ColorParams", "brightness_default")
		)
		self.rgb_bg_color = self.hsv_to_rgb(
			self.config.get_int("ColorParams", "bg_hue_default"),
			self.config.get_int("ColorParams", "bg_saturation_default"),
			self.config.get_int("ColorParams", "bg_brightness_default")
		)
		self.frame = None


	def initializeGL(self):
		self.logger.debug("Инициализация OpenGL")
		# Устанавливаем цвет фона из render_manager
		r, g, b = self.rgb_bg_color
		glClearColor(r, g, b, 1.0)  # Устанавливаем цвет фона
		glEnable(GL_POINT_SMOOTH)  # Сглаживание точек
		glEnable(GL_BLEND)
		glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)


	def resizeGL(self, w, h):
		self.logger.debug(f"Изменение размера холста: {w}x{h}")
		glViewport(0, 0, w, h)
		glMatrixMode(GL_PROJECTION)
		glLoadIdentity()
		glOrtho(-1, 1, -1, 1, -1, 1)  # Ортографическая проекция
		glMatrixMode(GL_MODELVIEW)
		glLoadIdentity()


	def paintGL(self):
		self.logger.debug("Отрисовка холста в paintGL")
		glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
		# Проверяем, есть ли кадр и включен ли флаг точек
		if (self.points_check and
				self.frame and
				"points" in self.frame):
			self.draw_points(self.frame["points"])


	def hsv_to_rgb(self, h, s, v):
		"""Преобразование цвета из HSV в RGB (значения от 0 до 1)."""
		self.logger.debug(f"Преобразование HSV ({h}, {s}, {v}) в RGB")
		h = h / 360.0  # Нормализация оттенка
		s = s / 100.0  # Нормализация насыщенности
		v = v / 100.0  # Нормализация яркости
		rgb = colorsys.hsv_to_rgb(h, s, v)
		return rgb  # Возвращает (r, g, b) в диапазоне [0, 1]

	def render_frame(self, frame):
		self.logger.debug("Отрисовка кадра")
		if not frame:
			self.logger.warning("Получен пустой кадр")
			return
		self.frame = frame
		if self.points_check and "points" in self.frame:
			self.draw_points(self.frame["points"])
		else:
			self.logger.warning("Кадр не содержит точек или points_check выключен")
		self.update()


	def draw_points(self, points):
		"""Отрисовка точек на холсте с использованием OpenGL."""
		self.logger.debug(f"Отрисовка {len(points)} точек с размером {self.points_size}")

		# Получаем размеры холста
		canvas_width = self.width()
		canvas_height = self.height()

		# Устанавливаем размер точек
		glPointSize(self.points_size)

		# Устанавливаем цвет точек (преобразуем HSV в RGB)
		glColor3f(*self.rgb_color)

		# Включаем режим отрисовки точек
		glBegin(GL_POINTS)
		for point in points:
			# Нормализуем координаты: переводим из [0, width/height] в [-1, 1]
			x = (point[0] / canvas_width) * 2.0 - 1.0
			y = 1.0 - (point[1] / canvas_height) * 2.0  # Инвертируем Y
			glVertex2f(x, y)
		glEnd()

	def set_points_check(self, flag):
		"""Установка флага отображения точке"""
		self.logger.debug(f"Установка флага отображения точек {flag}")
		self.points_check = flag
		self.update()

	def set_points_size(self, value):
		"""Установка размера точек"""
		self.logger.debug(f"Установка размера точек: {value}")
		self.points_size = value
		self.update()

	def set_lines_check(self, flag):
		"""Установка флага отображения линий"""
		self.logger.debug(f"Установка флага отображения линий {flag}")
		self.lines_check = flag
		self.update()

	def set_lines_width(self, value):
		"""Установка ширины линий"""
		self.logger.debug(f"Установка ширины линий: {value}")
		self.lines_width = value
		self.update()

	def set_fill_check(self, flag):
		"""Установка флага отображения заливки"""
		self.logger.debug(f"Установка флага отображения заливки {flag}")
		self.fill_check = flag
		self.update()

	def set_fill_variation(self, value):
		"""Установка разброса яркости заливки"""
		self.logger.debug(f"Установка разброса яркости заливки: {value}")
		self.fill_variation = value
		self.update()

	def set_hue(self, value):
		"""Установка оттенка основного цвета"""
		self.logger.debug(f"Установка оттенка основного цвета: {value}")
		self.hsv_color["h"] = value
		self.rgb_color = self.hsv_to_rgb(self.hsv_color["h"], self.hsv_color["s"], self.hsv_color["v"])
		self.update()

	def set_saturation(self, value):
		"""Установка насыщенности основного цвета"""
		self.logger.debug(f"Установка насыщенности основного цвета: {value}")
		self.hsv_color["s"] = value
		self.rgb_color = self.hsv_to_rgb(self.hsv_color["h"], self.hsv_color["s"], self.hsv_color["v"])
		self.update()

	def set_brightness(self, value):
		"""Установка яркости основного цвета"""
		self.logger.debug(f"Установка яркости основного цвета: {value}")
		self.hsv_color["v"] = value
		self.rgb_color = self.hsv_to_rgb(self.hsv_color["h"], self.hsv_color["s"], self.hsv_color["v"])
		self.update()

	def set_bg_hue(self, value):
		"""Установка оттенка цвета фона"""
		self.logger.debug(f"Установка оттенка цвета фона: {value}")
		self.hsv_bg_color["h"] = value
		self.rgb_bg_color = self.hsv_to_rgb(self.hsv_bg_color["h"], self.hsv_bg_color["s"], self.hsv_bg_color["v"])
		glClearColor(*self.rgb_bg_color, 1.0)
		self.update()

	def set_bg_saturation(self, value):
		"""Установка насыщенности цвета фона"""
		self.logger.debug(f"Установка насыщенности цвета фона: {value}")
		self.hsv_bg_color["s"] = value
		self.rgb_bg_color = self.hsv_to_rgb(self.hsv_bg_color["h"], self.hsv_bg_color["s"], self.hsv_bg_color["v"])
		glClearColor(*self.rgb_bg_color, 1.0)
		self.update()

	def set_bg_brightness(self, value):
		"""Установка яркости цвета фона"""
		self.logger.debug(f"Установка яркости цвета фона: {value}")
		self.hsv_bg_color["v"] = value
		self.rgb_bg_color = self.hsv_to_rgb(self.hsv_bg_color["h"], self.hsv_bg_color["s"], self.hsv_bg_color["v"])
		glClearColor(*self.rgb_bg_color, 1.0)
		self.update()

	def set_color(self, h, s, v):
		"""Установка основного цвета"""
		self.logger.debug(f"Установка основного цвета: {h=} {s=} {v=}")
		self.hsv_color = {"h": h, "s": s, "v": v}
		self.rgb_color = self.hsv_to_rgb(h, s, v)
		self.update()

	def set_bg_color(self, h, s, v):
		"""Установка цвета фона"""
		self.logger.debug(f"Установка цвета фона: {h=} {s=} {v=}")
		self.hsv_bg_color = {"h": h, "s": s, "v": v}
		self.rgb_bg_color = self.hsv_to_rgb(h, s, v)
		glClearColor(*self.rgb_bg_color, 1.0)
		self.update()
