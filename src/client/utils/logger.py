import os
import sys

from loguru import logger as loguru_logger


class Logger:
    _instance = None

    def __new__(cls, *args, **kwargs):
        if cls._instance is None:
            cls._instance = super(Logger, cls).__new__(cls)
            cls._instance._initialized = False
        return cls._instance

    def __init__(self):
        if self._initialized:
            return

        log_level = os.environ.get("LOG_LEVEL", "INFO")

        loguru_logger.remove()

        loguru_logger.add(
            sys.stderr,
            format="<green>{time:YYYY-MM-DD HH:mm:ss}</green> | <level>{level: <8}</level> | <cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> - <level>{message}</level>",
            level=log_level,
        )

        loguru_logger.add(
            "logs/app.log",
            rotation="10 MB",
            retention="1 week",
            level=log_level,
        )

        self.logger = loguru_logger
        self._initialized = True

    def debug(self, message, *args, **kwargs):
        return self.logger.debug(message, *args, **kwargs)

    def info(self, message, *args, **kwargs):
        return self.logger.info(message, *args, **kwargs)

    def warning(self, message, *args, **kwargs):
        return self.logger.warning(message, *args, **kwargs)

    def error(self, message, *args, **kwargs):
        return self.logger.error(message, *args, **kwargs)

    def critical(self, message, *args, **kwargs):
        return self.logger.critical(message, *args, **kwargs)


logger = Logger()

if __name__ == "__main__":
    logger.debug("This is a debug message.")
    logger.info("This is an info message.")
    logger.warning("This is a warning message.")
    logger.error("This is an error message.")
    logger.critical("This is a critical message.")
