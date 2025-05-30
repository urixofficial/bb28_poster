from loguru import logger
import sys


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