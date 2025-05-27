from loguru import logger
import sys

class RenderManager:
    def __init__(self, canvas, config_manager, log_level="ERROR"):
        self.canvas = canvas
        self.config = config_manager
        self.points_check = self.config.get_str("GenerationParams", "points_check").lower() == "true"
        self.points_size = self.config.get_int("GenerationParams", "points_size_default")
        self.lines_check = self.config.get_str("GenerationParams", "lines_check").lower() == "true"
        self.lines_width = self.config.get_int("GenerationParams", "lines_width_default")
        self.fill_check = self.config.get_str("GenerationParams", "fill_check").lower() == "true"
        self.fill_variation = self.config.get_int("GenerationParams", "fill_variation_default")
        self.color = {
            "h": self.config.get_int("ColorParams", "hue_default"),
            "s": self.config.get_int("ColorParams", "saturation_default"),
            "v": self.config.get_int("ColorParams", "brightness_default")
        }
        self.bg_color = {
            "h": self.config.get_int("ColorParams", "bg_hue_default"),
            "s": self.config.get_int("ColorParams", "bg_saturation_default"),
            "v": self.config.get_int("ColorParams", "bg_brightness_default")
        }
        self.frame = None
        self.set_logger(log_level)

    @staticmethod
    def set_logger(log_level):
        logger.remove()
        logger.add(sys.stderr, format="{time} | {level} | {name}:{line} | {message}", level=log_level)

    def render_frame(self, frame):
        logger.debug(f"Отрисовка кадра")
        self.frame = frame
        self.canvas.update()

    def set_points_check(self, flag):
        logger.debug(f"Установка флага отображения точек {flag}")
        self.points_check = flag

    def set_points_size(self, value):
        logger.debug(f"Установка размера точек: {value}")
        self.points_size = value

    def set_lines_check(self, flag):
        logger.debug(f"Установка флага отображения линий {flag}")
        self.lines_check = flag

    def set_lines_width(self, value):
        logger.debug(f"Установка ширины линий: {value}")
        self.lines_width = value

    def set_fill_check(self, flag):
        logger.debug(f"Установка флага отображения заливки {flag}")
        self.fill_check = flag

    def set_fill_variation(self, value):
        logger.debug(f"Установка разброса яркости заливки: {value}")
        self.fill_variation = value

    def set_hue(self, value):
        logger.debug(f"Установка оттенка основного цвета: {value}")
        self.color["h"] = value

    def set_saturation(self, value):
        logger.debug(f"Установка насыщенности основного цвета: {value}")
        self.color["s"] = value

    def set_brightness(self, value):
        logger.debug(f"Установка яркости основного цвета: {value}")
        self.color["v"] = value

    def set_bg_hue(self, value):
        logger.debug(f"Установка оттенка цвета фона: {value}")
        self.bg_color["h"] = value

    def set_bg_saturation(self, value):
        logger.debug(f"Установка насыщенности цвета фона: {value}")
        self.bg_color["s"] = value

    def set_bg_brightness(self, value):
        logger.debug(f"Установка яркости цвета фона: {value}")
        self.bg_color["v"] = value

    def set_color(self, h, s, v):
        logger.debug(f"Установка основного цвета: {h=} {s=} {v=}")
        self.color = {"h": h, "s": s, "v": v}

    def set_bg_color(self, h, s, v):
        logger.debug(f"Установка цвета фона: {h=} {s=} {v=}")
        self.bg_color = {"h": h, "s": s, "v": v}