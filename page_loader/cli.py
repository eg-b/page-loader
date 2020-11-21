import argparse

from page_loader import logging


def get_log_verbosity(level):
    level = level.lower()
    verbosity = logging.LEVELS.get(level)
    if verbosity is None:
        raise argparse.ArgumentTypeError(
            'incorrect logging level, try these: debug, info, error, warning')
    return verbosity


parser = argparse.ArgumentParser(description='Page loader')
parser.add_argument('-f', '--force', dest='force', action='store_true',
                    help="rewrite files if they already exist")
parser.add_argument('--output=', dest='output', metavar='DIR', default=None,
                    help='set download directory')
parser.add_argument('url', help='web address')
parser.add_argument('--log=', metavar='LEVEL', dest='level',
                    default=logging.INFO,
                    help='logging level: debug, warning, info, error',
                    type=get_log_verbosity)
parser.add_argument('--file=', dest='file', metavar='LOG_FILE',
                    default=None, help='log file name')
