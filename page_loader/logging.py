import logging
import sys


ERROR = 'error'
INFO = 'info'
WARNING = 'warning'
DEBUG = 'debug'


LEVELS = {
    ERROR: logging.ERROR,
    INFO: logging.INFO,
    WARNING: logging.WARNING,
    DEBUG: logging.DEBUG
}


def setup(level, log_file):
    errors_handler = logging.StreamHandler(stream=sys.stderr)
    errors_handler.setLevel(logging.ERROR)
    if log_file:
        main_handler = logging.FileHandler(log_file)
    else:
        main_handler = logging.StreamHandler(stream=sys.stdout)
    main_handler.setLevel(level)
    logging.basicConfig(format='%(asctime)s - %(levelname)s - %(message)s',
                        handlers=[errors_handler, main_handler])
