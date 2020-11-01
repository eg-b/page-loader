import argparse

from page_loader.logging import INFO, DEBUG, ERROR, WARNING
from page_loader import logging


parser = argparse.ArgumentParser(description='Page loader')
parser.add_argument('--output=', action='store',
                    dest='output', metavar='DIR', default=None,
                    help='set download directory')
parser.add_argument('url', help='web address')
parser.add_argument('--log=', metavar='LEVEL', dest='level', default=INFO,
                    help='set the logging level: debug, warning, info, error',
                    choices=logging.LEVELS.values(),
                    type=logging.LEVELS.get)
parser.add_argument('--file=', action='store', dest='file',
                    default=None, help='set log file name')
