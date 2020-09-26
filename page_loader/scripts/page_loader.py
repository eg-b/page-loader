#!/usr/bin/env python3
import sys

from page_loader.app import KnownError, page_load
from page_loader.cli import parser
from page_loader.log import fh, logger


def main():
    args = parser.parse_args()
    fh.setLevel(args.log.upper())
    logger.info('started')
    try:
        page_load(args.url, args.output)
    except KnownError:
        sys.exit(1)
    logger.info('finished')
    print('Success')
    sys.exit(0)


if __name__ == "__main__":
    main()
