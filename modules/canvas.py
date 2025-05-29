import colorsys
from PySide6.QtWidgets import QWidget
from pyqtgraph import PlotWidget, mkPen, mkBrush
from loguru import logger


class PyQtGraphCanvas(QWidget):
	def __init__(self, config_manager, log_level="INFO"):
		super().__init__()
		numeric_log_level = logger.level(log_level).no if isinstance(log_level, str) else log_level
		self.logger = logger.bind(module_level=numeric_log_level)
		self.config = config_manager

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
		self.rgb_color = self.hsv_to_rgb(
			self.hsv_color["h"], self.hsv_color["s"], self.hsv_color["v"]
		)
		self.rgb_bg_color = self.hsv_to_rgb(
			self.hsv_bg_color["h"], self.hsv_bg_color["s"], self.hsv_bg_color["v"]
		)
		self.frame_width = self.config.get_int("ImageParams", "width_default")
		self.frame_height = self.config.get_int("ImageParams", "height_default")
		self.frame = None

		# Создаем виджет PyQtGraph
		self.plot_widget = PlotWidget(self)
		self.plot_widget.setBackground(self.rgb_bg_color)
		self.plot_widget.setSizePolicy(self.sizePolicy())
		self.plot_widget.setMinimumSize(100, 100)

		# Настройка области отображения
		self.plot_item = self.plot_widget.getPlotItem()
		self.plot_item.setAspectLocked(True)
		self.plot_item.setRange(xRange=(0, self.frame_width), yRange=(0, self.frame_height))
		self.plot_item.invertY(False)

		# Отключаем оси
		self.plot_item.hideAxis('left')  # Скрываем ось Y
		self.plot_item.hideAxis('bottom')  # Скрываем ось X

		# Отключаем масштабирование и перемещение мышью
		self.plot_item.setMouseEnabled(x=False, y=False)

		# Отключаем автоматическое изменение диапазона
		self.plot_item.enableAutoRange(x=False, y=False)

		# Добавляем виджет в layout
		from PySide6.QtWidgets import QVBoxLayout
		layout = QVBoxLayout()
		layout.addWidget(self.plot_widget)
		self.setLayout(layout)

	@staticmethod
	def hsv_to_rgb(h, s, v):
		"""
		Convert HSV color to RGB color.

		Parameters:
		h (float): Hue (0-360)
		s (float): Saturation (0-100)
		v (float): Value/Brightness (0-100)

		Returns:
		tuple: RGB values (r, g, b) where each is in range (0-255)
		"""
		# Normalize inputs
		h = h % 360
		s = s / 100
		v = v / 100

		c = v * s
		x = c * (1 - abs((h / 60) % 2 - 1))
		m = v - c

		if 0 <= h < 60:
			r, g, b = c, x, 0
		elif 60 <= h < 120:
			r, g, b = x, c, 0
		elif 120 <= h < 180:
			r, g, b = 0, c, x
		elif 180 <= h < 240:
			r, g, b = 0, x, c
		elif 240 <= h < 300:
			r, g, b = x, 0, c
		else:
			r, g, b = c, 0, x

		# Scale to 0-255 range and convert to integers
		r = int((r + m) * 255)
		g = int((g + m) * 255)
		b = int((b + m) * 255)

		return (r, g, b)

	def render_frame(self, frame):
		"""Отрисовка кадра."""
		self.logger.debug("Отрисовка кадра")
		if not frame:
			self.logger.warning("Получен пустой кадр")
			return
		self.frame = frame
		self.plot_item.clear()  # Очищаем предыдущий контент
		if self.points_check and "points" in self.frame:
			self.draw_points(self.frame["points"])
		if self.lines_check and "lines" in self.frame:
			self.draw_lines(self.frame["lines"])
		if self.fill_check and "fill" in self.frame:
			self.draw_fill(self.frame["fill"])

	def draw_points(self, points):
		self.logger.debug(f"Отрисовка {len(points)} точек с размером {self.points_size}")
		self.logger.debug(f"Форма массива точек: {points.shape}")
		self.logger.debug(f"Цвет: {self.rgb_color}")
		x = points[:, 0]
		y = points[:, 1]
		pen = mkPen(color=self.rgb_color, width=0)  # Белый цвет для теста
		brush = mkBrush(color=self.rgb_color)
		self.plot_item.plot(x, y, pen=None, symbol='o', symbolSize=self.points_size, symbolPen=pen, symbolBrush=brush)
		self.logger.debug("Отрисовка завершена")


	def draw_lines(self, lines):
		self.logger.debug("Отрисовка линий")

	def draw_fill(self, lines):
		self.logger.debug("Отрисовка заливки")

	def save_image(self):
		"""Сохранение изображения."""
		self.logger.debug("Сохранение изображения")

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
		self.rgb_color = self.hsv_to_rgb(self.hsv_color["h"], self.hsv_color["s"], self.hsv_color["v"])
		self.render_frame(self.frame)

	def set_saturation(self, value):
		self.logger.debug(f"Установка насыщенности основного цвета: {value}")
		self.hsv_color["s"] = value
		self.rgb_color = self.hsv_to_rgb(self.hsv_color["h"], self.hsv_color["s"], self.hsv_color["v"])
		self.render_frame(self.frame)

	def set_brightness(self, value):
		self.logger.debug(f"Установка яркости основного цвета: {value}")
		self.hsv_color["v"] = value
		self.rgb_color = self.hsv_to_rgb(self.hsv_color["h"], self.hsv_color["s"], self.hsv_color["v"])
		self.render_frame(self.frame)

	def set_bg_hue(self, value):
		self.logger.debug(f"Установка оттенка цвета фона: {value}")
		self.hsv_bg_color["h"] = value
		self.rgb_bg_color = self.hsv_to_rgb(self.hsv_bg_color["h"], self.hsv_bg_color["s"], self.hsv_bg_color["v"])
		self.plot_widget.setBackground(self.rgb_bg_color)
		self.render_frame(self.frame)

	def set_bg_saturation(self, value):
		self.logger.debug(f"Установка насыщенности цвета фона: {value}")
		self.hsv_bg_color["s"] = value
		self.rgb_bg_color = self.hsv_to_rgb(self.hsv_bg_color["h"], self.hsv_bg_color["s"], self.hsv_bg_color["v"])
		self.plot_widget.setBackground(self.rgb_bg_color)
		self.render_frame(self.frame)

	def set_bg_brightness(self, value):
		self.logger.debug(f"Установка яркости цвета фона: {value}")
		self.hsv_bg_color["v"] = value
		self.rgb_bg_color = self.hsv_to_rgb(self.hsv_bg_color["h"], self.hsv_bg_color["s"], self.hsv_bg_color["v"])
		self.plot_widget.setBackground(self.rgb_bg_color)
		self.render_frame(self.frame)

	def set_color(self, h, s, v):
		self.logger.debug(f"Установка основного цвета: {h=} {s=} {v=}")
		self.hsv_color = {"h": h, "s": s, "v": v}
		self.rgb_color = self.hsv_to_rgb(h, s, v)
		self.render_frame(self.frame)

	def set_bg_color(self, h, s, v):
		self.logger.debug(f"Установка цвета фона: {h=} {s=} {v=}")
		self.hsv_bg_color = {"h": h, "s": s, "v": v}
		self.rgb_bg_color = self.hsv_to_rgb(h, s, v)
		self.plot_widget.setBackground(self.rgb_bg_color)
		self.render_frame(self.frame)
