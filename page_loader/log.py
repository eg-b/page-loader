import logging
import sys


logger = logging.getLogger('page-loader log')
logger.setLevel(logging.DEBUG)

ch = logging.StreamHandler(stream=sys.stderr)
ch.setLevel(logging.ERROR)

fh = logging.FileHandler('app.log')

formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
fh.setFormatter(formatter)
ch.setFormatter(formatter)

logger.addHandler(fh)
logger.addHandler(ch)