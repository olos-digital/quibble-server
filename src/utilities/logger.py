import json
import logging
import os
from logging.handlers import RotatingFileHandler


class JsonFormatter(logging.Formatter):
	def format(self, record):
		log_record = {
			"level": record.levelname,
			"time": self.formatTime(record, self.datefmt),
			"message": record.getMessage(),
			"pathname": record.pathname,
			"lineno": record.lineno
		}
		return json.dumps(log_record, ensure_ascii=False)


def setup_logger(name: str = "app_logger", log_file: str = "./logs/app.log"):
	logger = logging.getLogger(name)
	logger.setLevel(logging.INFO)

	# Remove all handlers associated with the logger to prevent duplicate logs
	if logger.hasHandlers():
		logger.handlers.clear()

	# Ensure log directory exists
	log_dir = os.path.dirname(log_file)
	if log_dir and not os.path.exists(log_dir):
		os.makedirs(log_dir, exist_ok=True)

	# File handler с JSON
	file_handler = RotatingFileHandler(log_file, maxBytes=5 * 1024 * 1024, backupCount=3)
	file_handler.setFormatter(JsonFormatter())

	# Console handler
	console_handler = logging.StreamHandler()
	console_formatter = logging.Formatter(
		'%(asctime)s - %(levelname)s - %(message)s (%(pathname)s:%(lineno)d)'
	)
	console_handler.setFormatter(console_formatter)

	logger.addHandler(file_handler)
	logger.addHandler(console_handler)

	return logger
