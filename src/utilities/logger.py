import logging
import json
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

    # File handler с JSON
    file_handler = RotatingFileHandler(log_file, maxBytes=5*1024*1024, backupCount=3)
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