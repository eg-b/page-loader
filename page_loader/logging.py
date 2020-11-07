import logging
import sys

from page_loader import app


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
    handlers = []
    err_handler = logging.StreamHandler(stream=sys.stderr)
    err_handler.setLevel(logging.ERROR)
    handlers.append(err_handler)
    if log_file:
        main_handler = logging.FileHandler(filename=log_file)
    else:
        main_handler = logging.StreamHandler(sys.stdout)
    handlers.append(main_handler)
    logging.root.handlers = []
    logging.basicConfig(level=level,
                        format='%(asctime)s - %(levelname)s - %(message)s',
                        handlers=handlers)


def get_param(level):
    level = level.lower()
    verbosity = LEVELS.get(level)
    if verbosity is None:
        raise app.KnownError('incorrect logging level,'
                             ' try these: debug, info, error, warning')
    return verbosity
