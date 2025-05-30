import sys
from PySide6.QtWidgets import QApplication
from modules.ui import MainUI
from PySide6.QtCore import QTimer
from modules.config_manager import ConfigManager
from modules.animation_manager import AnimationManager
from modules.render_manager import RenderManager
from loguru import logger
from modules.utils import set_logger

class MainApplication:
    def __init__(self, log_level):
        """Инициализация приложения"""
        set_logger()
        numeric_log_level = logger.level(log_level).no if isinstance(log_level, str) else log_level
        self.logger = logger.bind(module_level=numeric_log_level)
        logger.info("Инициализация приложения")

        self.app = QApplication(sys.argv)

        # Загрузга модулей
        self.config_manager = ConfigManager("config.ini", "INFO")
        self.ui = MainUI(self.config_manager, "INFO")
        self.animation_manager = AnimationManager(self.config_manager, "INFO")
        self.render_manager = RenderManager(self.config_manager, self.ui.canvas, "INFO")

        # Таймер для анимации
        self.animation_timer = QTimer()
        self.animation_timer.timeout.connect(self.update_animation)
        self.is_animating = False

        # Словарь для таймеров дебаунсинга
        self.debounce_timers = {}
        self.debounce_delay = 10  # Задержка дебаунсинга в миллисекундах

        self.set_signals()

    def create_debounce_timer(self, callback):
        """Создаёт и возвращает таймер для дебаунсинга с указанным callback."""
        timer = QTimer()
        timer.setSingleShot(True)
        timer.timeout.connect(callback)
        return timer

    def debounce(self, slider, callback):
        """Функция дебаунсинга для слайдера."""

        def handler():
            if slider in self.debounce_timers:
                self.debounce_timers[slider].stop()
            else:
                self.debounce_timers[slider] = self.create_debounce_timer(callback)
            self.debounce_timers[slider].start(self.debounce_delay)

        return handler

    def set_signals(self):
        """Подключение сигналов"""
        self.logger.info("Подключение сигналов")
        try:
            self.ui.width_input.valueChanged.connect(self.animation_manager.set_width)
            self.ui.width_input.valueChanged.connect(self.ui.update_canvas_size)
            self.ui.height_input.valueChanged.connect(self.animation_manager.set_height)
            self.ui.height_input.valueChanged.connect(self.ui.update_canvas_size)
            self.ui.fps_input.valueChanged.connect(self.animation_manager.set_fps)
            self.ui.duration_input.valueChanged.connect(self.animation_manager.set_duration)

            # Подключение сигналов для слайдеров с дебаунсингом
            self.ui.points_amount_slider.valueChanged.connect(
                self.debounce(self.ui.points_amount_slider,
                              lambda: self.animation_manager.set_points_amount(self.ui.points_amount_slider.value())))
            self.ui.points_check.toggled.connect(self.render_manager.set_points_check)
            self.ui.points_size_slider.valueChanged.connect(
                self.debounce(self.ui.points_size_slider,
                              lambda: self.render_manager.set_points_size(self.ui.points_size_slider.value())))
            self.ui.lines_check.toggled.connect(self.render_manager.set_lines_check)
            self.ui.lines_width_slider.valueChanged.connect(
                self.debounce(self.ui.lines_width_slider,
                              lambda: self.render_manager.set_lines_width(self.ui.lines_width_slider.value())))
            self.ui.fill_check.toggled.connect(self.render_manager.set_fill_check)
            self.ui.fill_variation_slider.valueChanged.connect(
                self.debounce(self.ui.fill_variation_slider,
                              lambda: self.render_manager.set_fill_variation(self.ui.fill_variation_slider.value())))
            self.ui.hue_slider.valueChanged.connect(
                self.debounce(self.ui.hue_slider,
                              lambda: self.render_manager.set_hue(self.ui.hue_slider.value())))
            self.ui.saturation_slider.valueChanged.connect(
                self.debounce(self.ui.saturation_slider,
                              lambda: self.render_manager.set_saturation(self.ui.saturation_slider.value())))
            self.ui.brightness_slider.valueChanged.connect(
                self.debounce(self.ui.brightness_slider,
                              lambda: self.render_manager.set_brightness(self.ui.brightness_slider.value())))
            self.ui.bg_hue_slider.valueChanged.connect(
                self.debounce(self.ui.bg_hue_slider,
                              lambda: self.render_manager.set_bg_hue(self.ui.bg_hue_slider.value())))
            self.ui.bg_saturation_slider.valueChanged.connect(
                self.debounce(self.ui.bg_saturation_slider,
                              lambda: self.render_manager.set_bg_saturation(self.ui.bg_saturation_slider.value())))
            self.ui.bg_brightness_slider.valueChanged.connect(
                self.debounce(self.ui.bg_brightness_slider,
                              lambda: self.render_manager.set_bg_brightness(self.ui.bg_brightness_slider.value())))
            self.ui.animation_speed_slider.valueChanged.connect(
                self.debounce(self.ui.animation_speed_slider,
                              lambda: self.animation_manager.set_animation_speed(
                                  self.ui.animation_speed_slider.value())))
            self.ui.transition_speed_slider.valueChanged.connect(
                self.debounce(self.ui.transition_speed_slider,
                              lambda: self.animation_manager.set_transition_speed(
                                  self.ui.transition_speed_slider.value())))

            # Подключение кнопок
            self.ui.generate_frame_btn.clicked.connect(self.generate_frame)
            self.ui.export_frame_btn.clicked.connect(self.export_frame)
            self.ui.start_animation_btn.clicked.connect(self.start_animation)
            self.ui.export_animation_btn.clicked.connect(self.export_animation)

        except AttributeError as e:
            logger.error(f"Ошибка при подключении сигналов: {e}")
            raise

    def generate_frame(self):
        """Генерация кадра"""
        self.logger.info("Запуск генерации кадра")
        self.animation_manager.init_frame()
        frame = self.animation_manager.get_frame()
        self.render_manager.render_frame(frame)

    def export_frame(self):
        self.logger.info("Экспорт кадра")
        self.render_manager.save_image()

    def start_animation(self):
        self.logger.info("Запуск/остановка анимации")
        if not self.is_animating:
            # Запускаем анимацию
            fps = self.ui.fps_input.value()
            if fps <= 0:
                self.logger.error("Частота кадров должна быть больше 0")
                return
            interval = 1000 // fps  # Интервал в миллисекундах
            self.animation_timer.start(interval)
            self.is_animating = True
            self.ui.start_animation_btn.setText("Остановка анимации")
        else:
            # Останавливаем анимацию
            self.animation_timer.stop()
            self.is_animating = False
            self.ui.start_animation_btn.setText("Запуск анимации")

    def update_animation(self):
        self.logger.debug("Обновление анимации")
        self.animation_manager.update_frame()
        frame = self.animation_manager.get_frame()
        self.render_manager.render_frame(frame)

    def export_animation(self):
        self.logger.debug("Экспорт анимации")
        # Логика экспорта анимации
        pass

    def run(self):
        self.ui.show()
        sys.exit(self.app.exec())

if __name__ == '__main__':
    app = MainApplication("INFO")
    app.run()