from PySide6.QtWidgets import QWidget
from pyqtgraph import PlotWidget, mkPen, mkBrush
from modules.utils import hsv_to_rgb
from loguru import logger


class PyQtGraphCanvas(QWidget):
	def __init__(self, config_manager, log_level="INFO"):
		super().__init__()
		numeric_log_level = logger.level(log_level).no if isinstance(log_level, str) else log_level
		self.logger = logger.bind(module_level=numeric_log_level)
		self.logger.debug("Инициализация холста")

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
		self.rgb_color = hsv_to_rgb(
			self.hsv_color["h"], self.hsv_color["s"], self.hsv_color["v"]
		)
		self.rgb_bg_color = hsv_to_rgb(
			self.hsv_bg_color["h"], self.hsv_bg_color["s"], self.hsv_bg_color["v"]
		)
		self.frame_width = self.config.get_int("ImageParams", "width_default")
		self.frame_height = self.config.get_int("ImageParams", "height_default")
		self.frame = None

		# Создаем виджет PyQtGraph
		self.plot_widget = PlotWidget(self)
		self.plot_widget.setBackground(self.rgb_bg_color)
		self.plot_widget.setSizePolicy(self.sizePolicy())

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
		x = points[:, 0]
		y = points[:, 1]
		pen = mkPen(color=self.rgb_color, width=0)  # Белый цвет для теста
		brush = mkBrush(color=self.rgb_color)
		self.plot_item.plot(x, y, pen=None, symbol='o', symbolSize=self.points_size, symbolPen=pen, symbolBrush=brush)

	def draw_lines(self, lines):
		self.logger.debug(f"Отрисовка {len(lines)} линий с толщиной {self.lines_width}")
		if not lines:
			self.logger.debug("Нет линий для отрисовки")
			return
		self.logger.debug(f"Цвет линий: {self.rgb_color}")
		pen = mkPen(color=self.rgb_color, width=self.lines_width)
		for line in lines:
			try:
				x = [line[0], line[2]]  # x-координаты начала и конца линии
				y = [line[1], line[3]]  # y-координаты начала и конца линии
				self.plot_item.plot(x, y, pen=pen, symbol=None)
			except (IndexError, TypeError) as e:
				self.logger.error(f"Ошибка при отрисовке линии {line}: {e}")

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
		self.plot_widget.setBackground(self.rgb_bg_color)
		self.render_frame(self.frame)

	def set_bg_saturation(self, value):
		self.logger.debug(f"Установка насыщенности цвета фона: {value}")
		self.hsv_bg_color["s"] = value
		self.rgb_bg_color = hsv_to_rgb(self.hsv_bg_color["h"], self.hsv_bg_color["s"], self.hsv_bg_color["v"])
		self.plot_widget.setBackground(self.rgb_bg_color)
		self.render_frame(self.frame)

	def set_bg_brightness(self, value):
		self.logger.debug(f"Установка яркости цвета фона: {value}")
		self.hsv_bg_color["v"] = value
		self.rgb_bg_color = hsv_to_rgb(self.hsv_bg_color["h"], self.hsv_bg_color["s"], self.hsv_bg_color["v"])
		self.plot_widget.setBackground(self.rgb_bg_color)
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
		self.plot_widget.setBackground(self.rgb_bg_color)
		self.render_frame(self.frame)
