from PySide6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QGridLayout, QGroupBox, QSlider, QCheckBox, QLineEdit, \
    QLabel, QPushButton, QSplitter
from PySide6.QtCore import Qt
from modules.canvas import OpenGLCanvas
from loguru import logger

class MainUI(QWidget):
    def __init__(self, config_manager, log_level="ERROR"):
        super().__init__()
        numeric_log_level = logger.level(log_level).no if isinstance(log_level, str) else log_level
        self.logger = logger.bind(module_level=numeric_log_level)
        self.config_manager = config_manager
        self.init_ui()

    def init_ui(self):
        self.logger.debug("Инициализация интерфейса")

        self.setWindowTitle(self.config_manager.get_str("Window", "title"))
        self.resize(
            self.config_manager.get_int("Window", "width"),
            self.config_manager.get_int("Window", "height")
        )

        # Основной layout с разделителем
        main_layout = QHBoxLayout()
        splitter = QSplitter(Qt.Orientation.Horizontal)

        # Левая часть: OpenGL предпросмотр
        self.canvas = OpenGLCanvas(self.config_manager, log_level="DEBUG")
        splitter.addWidget(self.canvas)

        # Правая часть: Панель управления
        control_panel = QWidget()
        control_layout = QVBoxLayout()
        control_layout.setSpacing(30)

        # Блок "Параметры изображения"
        image_params = QGroupBox("Параметры изображения")
        image_params_layout = QGridLayout()

        width_label = QLabel("Ширина (px):")
        self.width_input = QLineEdit(str(self.config_manager.get_int("ImageParams", "default_width")))
        height_label = QLabel("Высота (px):")
        self.height_input = QLineEdit(str(self.config_manager.get_int("ImageParams", "default_height")))
        fps_label = QLabel("Кадров/с:")
        self.fps_input = QLineEdit(str(self.config_manager.get_int("ImageParams", "default_fps")))
        duration_label = QLabel("Длительность (с):")
        self.duration_input = QLineEdit(str(self.config_manager.get_int("ImageParams", "default_duration")))

        image_params_layout.addWidget(width_label, 0, 0)
        image_params_layout.addWidget(self.width_input, 0, 1)
        image_params_layout.addWidget(height_label, 0, 2)
        image_params_layout.addWidget(self.height_input, 0, 3)
        image_params_layout.addWidget(fps_label, 1, 0)
        image_params_layout.addWidget(self.fps_input, 1, 1)
        image_params_layout.addWidget(duration_label, 1, 2)
        image_params_layout.addWidget(self.duration_input, 1, 3)

        image_params.setLayout(image_params_layout)
        control_layout.addWidget(image_params)

        # Блок "Параметры генерации"
        gen_params = QGroupBox("Параметры генерации")
        gen_params_layout = QGridLayout()

        points_amount_label = QLabel("Количество:")
        self.points_amount_slider = QSlider(Qt.Orientation.Horizontal)
        self.points_amount_slider.setRange(
            self.config_manager.get_int("GenerationParams", "points_amount_min"),
            self.config_manager.get_int("GenerationParams", "points_amount_max")
        )
        self.points_amount_slider.setValue(self.config_manager.get_int("GenerationParams", "points_amount_default"))
        self.points_amount_value = QLabel(str(self.config_manager.get_int("GenerationParams", "points_amount_default")))
        self.points_amount_slider.valueChanged.connect(lambda: self.points_amount_value.setText(str(self.points_amount_slider.value())))

        self.points_check = QCheckBox("Точки")
        points_size_label = QLabel("Размер")
        self.points_size_slider = QSlider(Qt.Orientation.Horizontal)
        self.points_size_slider.setRange(
            self.config_manager.get_int("GenerationParams", "points_size_min"),
            self.config_manager.get_int("GenerationParams", "points_size_max")
        )
        self.points_size_slider.setValue(self.config_manager.get_int("GenerationParams", "points_size_default"))
        self.points_size_value = QLabel(str(self.config_manager.get_int("GenerationParams", "points_size_default")))
        self.points_size_slider.valueChanged.connect(
            lambda: self.points_size_value.setText(str(self.points_size_slider.value())))

        self.lines_check = QCheckBox("Линии")
        lines_width_label = QLabel("Толщина:")
        self.lines_width_slider = QSlider(Qt.Orientation.Horizontal)
        self.lines_width_slider.setRange(
            self.config_manager.get_int("GenerationParams", "lines_width_min"),
            self.config_manager.get_int("GenerationParams", "lines_width_max")
        )
        self.lines_width_slider.setValue(self.config_manager.get_int("GenerationParams", "lines_width_default"))
        self.lines_width_value = QLabel(str(self.config_manager.get_int("GenerationParams", "lines_width_default")))
        self.lines_width_slider.valueChanged.connect(
            lambda: self.lines_width_value.setText(str(self.lines_width_slider.value())))

        self.fill_check = QCheckBox("Заливка")
        fill_label = QLabel("Разброс:")
        self.fill_variation_slider = QSlider(Qt.Orientation.Horizontal)
        self.fill_variation_slider.setRange(
            self.config_manager.get_int("GenerationParams", "fill_variation_min"),
            self.config_manager.get_int("GenerationParams", "fill_variation_max")
        )
        self.fill_variation_slider.setValue(self.config_manager.get_int("GenerationParams", "fill_variation_default"))
        self.fill_variation_value = QLabel(str(self.config_manager.get_int("GenerationParams", "fill_variation_default")))
        self.fill_variation_slider.valueChanged.connect(lambda: self.fill_variation_value.setText(str(self.fill_variation_slider.value())))

        gen_params_layout.addWidget(points_amount_label, 0, 0)
        gen_params_layout.addWidget(self.points_amount_slider, 0, 1, 1, 2)
        gen_params_layout.addWidget(self.points_amount_value, 0, 3)
        gen_params_layout.addWidget(self.points_check, 1, 0)
        gen_params_layout.addWidget(points_size_label, 1, 1)
        gen_params_layout.addWidget(self.points_size_slider, 1, 2)
        gen_params_layout.addWidget(self.points_size_value, 1, 3)
        gen_params_layout.addWidget(self.lines_check, 2, 0)
        gen_params_layout.addWidget(lines_width_label, 2, 1)
        gen_params_layout.addWidget(self.lines_width_slider, 2, 2)
        gen_params_layout.addWidget(self.lines_width_value, 2, 3)
        gen_params_layout.addWidget(self.fill_check, 3, 0)
        gen_params_layout.addWidget(fill_label, 3, 1)
        gen_params_layout.addWidget(self.fill_variation_slider, 3, 2)
        gen_params_layout.addWidget(self.fill_variation_value, 3, 3)

        gen_params.setLayout(gen_params_layout)
        control_layout.addWidget(gen_params)

        # Блок "Основной цвет"
        color_group = QGroupBox("Основной цвет")
        color_layout = QGridLayout()

        hue_label = QLabel("Оттенок:")
        self.hue_slider = QSlider(Qt.Orientation.Horizontal)
        self.hue_slider.setRange(
            self.config_manager.get_int("ColorParams", "hue_min"),
            self.config_manager.get_int("ColorParams", "hue_max")
        )
        self.hue_slider.setValue(self.config_manager.get_int("ColorParams", "hue_default"))
        self.hue_value = QLabel(str(self.config_manager.get_int("ColorParams", "hue_default")))
        self.hue_slider.valueChanged.connect(lambda: self.hue_value.setText(str(self.hue_slider.value())))

        saturation_label = QLabel("Насыщенность:")
        self.saturation_slider = QSlider(Qt.Orientation.Horizontal)
        self.saturation_slider.setRange(
            self.config_manager.get_int("ColorParams", "saturation_min"),
            self.config_manager.get_int("ColorParams", "saturation_max")
        )
        self.saturation_slider.setValue(self.config_manager.get_int("ColorParams", "saturation_default"))
        self.saturation_value = QLabel(str(self.config_manager.get_int("ColorParams", "saturation_default")))
        self.saturation_slider.valueChanged.connect(
            lambda: self.saturation_value.setText(str(self.saturation_slider.value())))

        brightness_label = QLabel("Яркость:")
        self.brightness_slider = QSlider(Qt.Orientation.Horizontal)
        self.brightness_slider.setRange(
            self.config_manager.get_int("ColorParams", "brightness_min"),
            self.config_manager.get_int("ColorParams", "brightness_max")
        )
        self.brightness_slider.setValue(self.config_manager.get_int("ColorParams", "brightness_default"))
        self.brightness_value = QLabel(str(self.config_manager.get_int("ColorParams", "brightness_default")))
        self.brightness_slider.valueChanged.connect(
            lambda: self.brightness_value.setText(str(self.brightness_slider.value())))

        color_layout.addWidget(hue_label, 0, 0)
        color_layout.addWidget(self.hue_slider, 0, 1)
        color_layout.addWidget(self.hue_value, 0, 2)
        color_layout.addWidget(saturation_label, 1, 0)
        color_layout.addWidget(self.saturation_slider, 1, 1)
        color_layout.addWidget(self.saturation_value, 1, 2)
        color_layout.addWidget(brightness_label, 2, 0)
        color_layout.addWidget(self.brightness_slider, 2, 1)
        color_layout.addWidget(self.brightness_value, 2, 2)

        color_group.setLayout(color_layout)
        control_layout.addWidget(color_group)

        # Блок "Цвет фона"
        bg_color_group = QGroupBox("Цвет фона")
        bg_color_layout = QGridLayout()

        bg_hue_label = QLabel("Оттенок:")
        self.bg_hue_slider = QSlider(Qt.Orientation.Horizontal)
        self.bg_hue_slider.setRange(
            self.config_manager.get_int("ColorParams", "bg_hue_min"),
            self.config_manager.get_int("ColorParams", "bg_hue_max")
        )
        self.bg_hue_slider.setValue(self.config_manager.get_int("ColorParams", "bg_hue_default"))
        self.bg_hue_value = QLabel(str(self.config_manager.get_int("ColorParams", "bg_hue_default")))
        self.bg_hue_slider.valueChanged.connect(lambda: self.bg_hue_value.setText(str(self.bg_hue_slider.value())))

        bg_saturation_label = QLabel("Насыщенность:")
        self.bg_saturation_slider = QSlider(Qt.Orientation.Horizontal)
        self.bg_saturation_slider.setRange(
            self.config_manager.get_int("ColorParams", "bg_saturation_min"),
            self.config_manager.get_int("ColorParams", "bg_saturation_max")
        )
        self.bg_saturation_slider.setValue(self.config_manager.get_int("ColorParams", "bg_saturation_default"))
        self.bg_saturation_value = QLabel(str(self.config_manager.get_int("ColorParams", "bg_saturation_default")))
        self.bg_saturation_slider.valueChanged.connect(
            lambda: self.bg_saturation_value.setText(str(self.bg_saturation_slider.value())))

        bg_brightness_label = QLabel("Яркость:")
        self.bg_brightness_slider = QSlider(Qt.Orientation.Horizontal)
        self.bg_brightness_slider.setRange(
            self.config_manager.get_int("ColorParams", "bg_brightness_min"),
            self.config_manager.get_int("ColorParams", "bg_brightness_max")
        )
        self.bg_brightness_slider.setValue(self.config_manager.get_int("ColorParams", "bg_brightness_default"))
        self.bg_brightness_value = QLabel(str(self.config_manager.get_int("ColorParams", "bg_brightness_default")))
        self.bg_brightness_slider.valueChanged.connect(
            lambda: self.bg_brightness_value.setText(str(self.bg_brightness_slider.value())))

        bg_color_layout.addWidget(bg_hue_label, 0, 0)
        bg_color_layout.addWidget(self.bg_hue_slider, 0, 1)
        bg_color_layout.addWidget(self.bg_hue_value, 0, 2)
        bg_color_layout.addWidget(bg_saturation_label, 1, 0)
        bg_color_layout.addWidget(self.bg_saturation_slider, 1, 1)
        bg_color_layout.addWidget(self.bg_saturation_value, 1, 2)
        bg_color_layout.addWidget(bg_brightness_label, 2, 0)
        bg_color_layout.addWidget(self.bg_brightness_slider, 2, 1)
        bg_color_layout.addWidget(self.bg_brightness_value, 2, 2)

        bg_color_group.setLayout(bg_color_layout)
        control_layout.addWidget(bg_color_group)

        # Блок "Параметры анимации"
        animation_params = QGroupBox("Параметры анимации")
        animation_params_layout = QGridLayout()

        transition_speed_label = QLabel("Скорость переходов:")
        self.transition_speed_slider = QSlider(Qt.Orientation.Horizontal)
        self.transition_speed_slider.setRange(
            self.config_manager.get_int("AnimationParams", "transition_speed_min"),
            self.config_manager.get_int("AnimationParams", "transition_speed_max")
        )
        self.transition_speed_slider.setValue(self.config_manager.get_int("AnimationParams", "transition_speed_default"))
        self.transition_speed_value = QLabel(str(self.config_manager.get_int("AnimationParams", "transition_speed_default")))
        self.transition_speed_slider.valueChanged.connect(
            lambda: self.transition_speed_value.setText(str(self.transition_speed_slider.value())))

        animation_speed_label = QLabel("Скорость анимации:")
        self.animation_speed_slider = QSlider(Qt.Orientation.Horizontal)
        self.animation_speed_slider.setRange(
            self.config_manager.get_int("AnimationParams", "animation_speed_min"),
            self.config_manager.get_int("AnimationParams", "animation_speed_max")
        )
        self.animation_speed_slider.setValue(self.config_manager.get_int("AnimationParams", "animation_speed_default"))
        self.animation_speed_value = QLabel(str(self.config_manager.get_int("AnimationParams", "animation_speed_default")))
        self.animation_speed_slider.valueChanged.connect(
            lambda: self.animation_speed_value.setText(str(self.animation_speed_slider.value())))

        animation_params_layout.addWidget(transition_speed_label, 0, 0)
        animation_params_layout.addWidget(self.transition_speed_slider, 0, 1)
        animation_params_layout.addWidget(self.transition_speed_value, 0, 2)
        animation_params_layout.addWidget(animation_speed_label, 1, 0)
        animation_params_layout.addWidget(self.animation_speed_slider, 1, 1)
        animation_params_layout.addWidget(self.animation_speed_value, 1, 2)

        animation_params.setLayout(animation_params_layout)
        control_layout.addWidget(animation_params)

        # Кнопки действий
        actions_group = QGroupBox("Действия")
        actions_layout = QGridLayout()

        self.generate_frame_btn = QPushButton("Сгенерировать кадр")
        self.export_frame_btn = QPushButton("Экспортировать кадр")
        self.start_animation_btn = QPushButton("Запустить анимацию")
        self.export_animation_btn = QPushButton("Экспортировать анимацию")

        actions_layout.addWidget(self.generate_frame_btn, 0, 0)
        actions_layout.addWidget(self.export_frame_btn, 0, 1)
        actions_layout.addWidget(self.start_animation_btn, 1, 0)
        actions_layout.addWidget(self.export_animation_btn, 1, 1)

        actions_group.setLayout(actions_layout)
        control_layout.addWidget(actions_group)

        control_panel.setLayout(control_layout)
        splitter.addWidget(control_panel)

        # Устанавливаем пропорции разделителя
        main_layout.addWidget(splitter)
        self.setLayout(main_layout)