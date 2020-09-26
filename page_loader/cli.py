import argparse

from page_loader.app import CURRENT_DIR

parser = argparse.ArgumentParser(description='Page loader')
parser.add_argument('--output=', action='store',
                    dest='output', metavar='DIR', default=CURRENT_DIR,
                    help='set download directory')
parser.add_argument('url', help='web address')
parser.add_argument('--log=', metavar='LEVEL', dest='lvl',
                    help='set the logging level: debug, warning, info')
