#!/usr/bin/env python3
import sys
import logging

from page_loader import logging as logging_
from page_loader.app import KnownError, page_load
from page_loader import cli


def main():
    try:
        args = cli.parser.parse_args()
    except KnownError as e:
        logging.error(e)
        sys.exit(1)
    logging_.setup(level=args.level, log_file=args.file)
    logging.info('started')
    try:
        page_load(args.url, args.output, args.force)
    except KnownError as e:
        logging.debug(e, exc_info=sys.exc_info())
        logging.error(e)
        sys.exit(1)
    logging.info('finished')


if __name__ == "__main__":
    main()
