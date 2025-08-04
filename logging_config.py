import logging
import logging.config
import sys

def setup_logging():
    LOGGING_CONFIG = {
        'version': 1,
        'disable_existing_loggers': False,
        'formatters': {
            'default': {
                'format': '%(levelname)s - %(asctime)s - %(filename)s - line:%(lineno)d - func:%(funcName)s - %(message)s',
                'datefmt': '%Y-%m-%d %H:%M:%S'
            },
        },
        'handlers': {
            'console': {
                'class': 'logging.StreamHandler',
                'formatter': 'default',
                'stream': sys.stdout,
            },
            # Add a file handler
            'file': {
                'class': 'logging.handlers.RotatingFileHandler',
                'formatter': 'default',
                'filename': 'app.log', # The log file
                'maxBytes': 10485760,  # 10 MB
                'backupCount': 5,      # Keep 5 backup files
                'encoding': 'utf-8',
            },
        },
        'root': {
            'level': 'INFO',
            # Add the 'file' handler to the root logger
            'handlers': ['console', 'file'] 
        }
    }
    logging.config.dictConfig(LOGGING_CONFIG)