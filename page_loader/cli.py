import argparse

from progress.bar import Bar

from page_loader.logging import INFO, DEBUG, ERROR, WARNING
from page_loader import logging


parser = argparse.ArgumentParser(description='Page loader')
parser.add_argument('-f', '--force', dest='force', action='store_true',
                    help="rewrite files if they already exist")
parser.add_argument('--output=', dest='output', metavar='DIR', default=None,
                    help='set download directory')
parser.add_argument('url', help='web address')
parser.add_argument('--log=', metavar='LEVEL', dest='level', default=INFO,
                    help='logging level: debug, warning, info, error',
                    choices=logging.LEVELS.values(),
                    type=logging.LEVELS.get)
parser.add_argument('--file=', dest='file', metavar='LOG_FILE',
                    default=None, help='log file name')


def setup_bar(max):
    return Bar('Processing ', max=max, suffix='%(percent)d%%')

