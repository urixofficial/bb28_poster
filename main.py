import sys
from PySide6.QtWidgets import QApplication
from modules.ui import MainUI
from modules.config_manager import ConfigManager
from modules.animation_manager import AnimationManager
from loguru import logger

class MainApplication:
    def __init__(self, log_level):
        """Инициализация приложения"""
        self.set_logger()
        logger.debug("Инициализация приложения")
        self.app = QApplication(sys.argv)

        # Загрузга модулей
        self.config_manager = ConfigManager("config.ini", "INFO")
        self.ui = MainUI(self.config_manager, "INFO")
        self.animation_manager = AnimationManager(self.config_manager, "INFO")

        self.set_signals()


    @staticmethod
    def set_logger():
        """Настройка логгера"""
        logger.remove()
        log_format = ("<green>{time:YYYY-MM-DD HH:mm:ss}</green> | "
                      "<level>{level: <8}</level> | "
                      "<cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> | "
                      "<level>{message}</level>")
        logger.add(
            sys.stderr,
            format=log_format,
            filter=lambda record: record["extra"].get("module_level", 10) <= record["level"].no
        )

    def set_signals(self):
        """Подключение сигналов"""
        self.ui.width_input.textChanged.connect(self.animation_manager.set_width)
        self.ui.height_input.textChanged.connect(self.animation_manager.set_height)
        self.ui.points_amount_slider.valueChanged.connect(self.animation_manager.set_points_amount)
        self.ui.points_check.toggled.connect(self.ui.canvas.set_points_check)
        self.ui.points_size_slider.valueChanged.connect(self.ui.canvas.set_points_size)
        self.ui.lines_check.toggled.connect(self.ui.canvas.set_lines_check)
        self.ui.lines_width_slider.valueChanged.connect(self.ui.canvas.set_lines_width)
        self.ui.fill_check.toggled.connect(self.ui.canvas.set_fill_check)
        self.ui.fill_variation_slider.valueChanged.connect(self.ui.canvas.set_fill_variation)
        self.ui.hue_slider.valueChanged.connect(self.ui.canvas.set_hue)
        self.ui.saturation_slider.valueChanged.connect(self.ui.canvas.set_saturation)
        self.ui.brightness_slider.valueChanged.connect(self.ui.canvas.set_brightness)
        self.ui.bg_hue_slider.valueChanged.connect(self.ui.canvas.set_bg_hue)
        self.ui.bg_saturation_slider.valueChanged.connect(self.ui.canvas.set_bg_saturation)
        self.ui.bg_brightness_slider.valueChanged.connect(self.ui.canvas.set_bg_brightness)
        self.ui.animation_speed_slider.valueChanged.connect(self.animation_manager.set_animation_speed)
        self.ui.transition_speed_slider.valueChanged.connect(self.animation_manager.set_transition_speed)
        self.ui.generate_frame_btn.clicked.connect(self.generate_frame)

    def generate_frame(self):
        """Генерация кадра"""
        logger.debug("Запуск генерации кадра")
        self.animation_manager.init_frame()
        frame = self.animation_manager.get_frame()
        self.ui.canvas.render_frame(frame)

    def run(self):
        self.ui.show()
        sys.exit(self.app.exec())

if __name__ == '__main__':
    app = MainApplication("DEBUG")
    app.run()