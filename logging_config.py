import os
import logging
import logging.config
import sys


def setup_logging():
    # Ensure the log directory exists
    log_directory = os.path.dirname("logs/app.log")  # TODO: Move to .env via Config
    if log_directory and not os.path.exists(log_directory):
        os.makedirs(log_directory)

    LOGGING_CONFIG = {
        "version": 1,
        "disable_existing_loggers": False,
        "formatters": {
            "default": {
                "format": "%(levelname)s - %(asctime)s - %(filename)s - line:%(lineno)d - func:%(funcName)s - %(message)s",
                "datefmt": "%Y-%m-%d %H:%M:%S",
            },
            "json": {
                "class": "pythonjsonlogger.jsonlogger.JsonFormatter",
                "format": "%(asctime)s %(levelname)s %(name)s %(module)s %(funcName)s %(lineno)d %(message)s",
            },
        },
        "handlers": {
            "console": {
                "class": "logging.StreamHandler",
                "formatter": "default",
                "stream": sys.stdout,
            },
            # Add a file handler
            "file": {
                "class": "logging.handlers.RotatingFileHandler",
                "formatter": "json",
                "filename": "logs/app.log",  # The log file
                "maxBytes": 1024 * 2,  # 2 MB
                "backupCount": 5,  # Keep 5 backup files
                "encoding": "utf-8",
            },
        },
        "root": {"level": "INFO", "handlers": ["console", "file"]},
    }

    try:
        logging.config.dictConfig(LOGGING_CONFIG)
    except (ValueError, ModuleNotFoundError) as e:
        print(f"Error configuring logging: {e}")
        print(
            "Please ensure 'python-json-logger' is installed (`pip install python-json-logger`)."
        )
        # Handle the error gracefully, maybe fall back to basic logging
        logging.basicConfig(level=logging.INFO)
        logging.error("Fell back to basic logging configuration.")
