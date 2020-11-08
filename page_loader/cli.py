import argparse

from page_loader import logging


parser = argparse.ArgumentParser(description='Page loader')
parser.add_argument('-f', '--force', dest='force', action='store_true',
                    help="rewrite files if they already exist")
parser.add_argument('--output=', dest='output', metavar='DIR', default=None,
                    help='set download directory')
parser.add_argument('url', help='web address')
parser.add_argument('--log=', metavar='LEVEL', dest='level',
                    default=logging.INFO,
                    help='logging level: debug, warning, info, error',
                    type=logging.get_param)
parser.add_argument('--file=', dest='file', metavar='LOG_FILE',
                    default=None, help='log file name')
