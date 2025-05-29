import sys
from PySide6.QtWidgets import QApplication
from modules.ui import MainUI
from PySide6.QtCore import QTimer
from modules.config_manager import ConfigManager
from modules.animation_manager import AnimationManager
from loguru import logger

class MainApplication:
    def __init__(self, log_level):
        """Инициализация приложения"""
        self.set_logger()
        numeric_log_level = logger.level(log_level).no if isinstance(log_level, str) else log_level
        self.logger = logger.bind(module_level=numeric_log_level)
        logger.debug("Инициализация приложения")

        self.app = QApplication(sys.argv)

        # Загрузга модулей
        self.config_manager = ConfigManager("config.ini", "INFO")
        self.ui = MainUI(self.config_manager, "INFO")
        self.animation_manager = AnimationManager(self.config_manager, "INFO")

        # Таймер для анимации
        self.animation_timer = QTimer()
        self.animation_timer.timeout.connect(self.update_animation)
        self.is_animating = False

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
        self.logger.debug("Подключение сигналов")
        try:
            self.ui.width_input.valueChanged.connect(self.animation_manager.set_width)
            self.ui.width_input.valueChanged.connect(self.ui.update_canvas_size)
            self.ui.height_input.valueChanged.connect(self.animation_manager.set_height)
            self.ui.height_input.valueChanged.connect(self.ui.update_canvas_size)
            self.ui.fps_input.valueChanged.connect(self.animation_manager.set_fps)
            self.ui.duration_input.valueChanged.connect(self.animation_manager.set_duration)
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
            self.ui.export_frame_btn.clicked.connect(self.export_frame)
            self.ui.start_animation_btn.clicked.connect(self.start_animation)
            self.ui.export_animation_btn.clicked.connect(self.export_animation)
        except AttributeError as e:
            logger.error(f"Ошибка при подключении сигналов: {e}")
            raise

    def generate_frame(self):
        """Генерация кадра"""
        self.logger.debug("Запуск генерации кадра")
        self.animation_manager.init_frame()
        frame = self.animation_manager.get_frame()
        self.ui.canvas.render_frame(frame)

    def export_frame(self):
        self.logger.debug("Экспорт кадра")
        self.ui.canvas.save_image()

    def start_animation(self):
        self.logger.debug("Запуск/остановка анимации")
        if not self.is_animating:
            # Запускаем анимацию
            fps = self.ui.fps_input.value()
            if fps <= 0:
                self.logger.error("Частота кадров должна быть больше 0")
                return
            interval = 1000 // fps  # Интервал в миллисекундах
            self.animation_timer.start(interval)
            self.is_animating = True
            self.ui.start_animation_btn.setText("Остановить анимацию")
        else:
            # Останавливаем анимацию
            self.animation_timer.stop()
            self.is_animating = False
            self.ui.start_animation_btn.setText("Запустить анимацию")

    def update_animation(self):
        self.logger.debug("Обновление анимации")
        self.animation_manager.update_frame()
        frame = self.animation_manager.get_frame()
        self.ui.canvas.render_frame(frame)

    def export_animation(self):
        self.logger.debug("Экспорт анимации")
        # Логика экспорта анимации
        pass

    def run(self):
        self.ui.show()
        sys.exit(self.app.exec())

if __name__ == '__main__':
    app = MainApplication("DEBUG")
    app.run()