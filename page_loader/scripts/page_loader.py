#!/usr/bin/env python3
from page_loader.cli import parser
from page_loader.app import page_load
import logging
import sys


def main():
    args = parser.parse_args()
    logging.basicConfig(format='%(asctime)s %(levelname)s: %(message)s',
                        level=getattr(logging, args.log.upper()))
    logging.info('started')
    page_load(args.url, args.output)
    logging.info('finished')
    sys.exit(0)


if __name__ == "__main__":
    main()
