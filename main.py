import sys
from PySide6.QtWidgets import QApplication

from modules.render_manager import RenderManager
from modules.ui import MainUI
from modules.config_manager import ConfigManager
from modules.animation_manager import AnimationManager
from loguru import logger

class MainApplication:
    def __init__(self):
        logger.debug("Инициализация приложения")
        self.app = QApplication(sys.argv)

        # Загрузга модулей
        self.config_manager = ConfigManager("config.ini", "DEBUG")
        self.ui = MainUI(self.config_manager, "DEBUG")
        self.render_manager = RenderManager(self.ui.canvas, self.config_manager, "DEBUG")
        self.animation_manager = AnimationManager(self.config_manager, "DEBUG")
        self.render_manager = RenderManager(self.ui.canvas, self.config_manager, "DEBUG")
        self.animation_manager = AnimationManager(self.config_manager, "DEBUG")

        # Подключение сигналов
        self.ui.generate_frame_btn.clicked.connect(self.generate_frame)
        self.ui.points_amount_slider.valueChanged.connect(self.animation_manager.set_points_amount)
        self.ui.points_check.toggled.connect(self.render_manager.set_points_check)
        self.ui.points_size_slider.valueChanged.connect(self.render_manager.set_points_size)
        self.ui.lines_check.toggled.connect(self.render_manager.set_lines_check)
        self.ui.lines_width_slider.valueChanged.connect(self.render_manager.set_lines_width)
        self.ui.fill_check.toggled.connect(self.render_manager.set_fill_check)
        self.ui.fill_variation_slider.valueChanged.connect(self.render_manager.set_fill_variation)
        self.ui.hue_slider.valueChanged.connect(self.render_manager.set_hue)
        self.ui.saturation_slider.valueChanged.connect(self.render_manager.set_saturation)
        self.ui.brightness_slider.valueChanged.connect(self.render_manager.set_brightness)
        self.ui.bg_hue_slider.valueChanged.connect(self.render_manager.set_bg_hue)
        self.ui.bg_saturation_slider.valueChanged.connect(self.render_manager.set_bg_saturation)
        self.ui.bg_brightness_slider.valueChanged.connect(self.render_manager.set_bg_brightness)
        self.ui.animation_speed_slider.valueChanged.connect(self.animation_manager.set_animation_speed)
        self.ui.transition_speed_slider.valueChanged.connect(self.animation_manager.set_transition_speed)

    def generate_frame(self):
        logger.debug("Запуск генерации кадра")
        self.animation_manager.init_frame()
        frame = self.animation_manager.get_frame()
        self.render_manager.render_frame(frame)

    def run(self):
        self.ui.show()
        sys.exit(self.app.exec())

if __name__ == '__main__':
    app = MainApplication()
    app.run()