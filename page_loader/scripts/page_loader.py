#!/usr/bin/env python3
import logging
import sys

import page_loader.logging
from page_loader import cli
from page_loader.app import KnownError, download_page


def main():
    args = cli.parser.parse_args()
    page_loader.logging.setup(level=args.level, log_file=args.file)
    logging.info('started')
    try:
        download_page(url=args.url, output_directory=args.output,
                      overwrite=args.force)
    except KnownError as e:
        logging.debug(e, exc_info=sys.exc_info())
        logging.error(e)
        sys.exit(1)
    logging.info('finished')


if __name__ == "__main__":
    main()
