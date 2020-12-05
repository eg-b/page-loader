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
    err_handler = logging.StreamHandler(stream=sys.stderr)
    err_handler.setLevel(logging.ERROR)
    if log_file:
        main_handler = logging.FileHandler(filename=log_file)
    else:
        main_handler = logging.StreamHandler(sys.stdout)
    logging.root.handlers = []
    logging.basicConfig(level=level,
                        format='%(asctime)s - %(levelname)s - %(message)s',
                        handlers=[main_handler, err_handler])
