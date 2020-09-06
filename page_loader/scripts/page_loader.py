#!/usr/bin/env python3
from page_loader.cli import parser
from page_loader.app import page_load
import logging


def main():
    args = parser.parse_args()
    logging.basicConfig(format='%(asctime)s %(levelname)s: %(message)s',
                        filename='./app_log',
                        level=getattr(logging, args.log.upper()))
    logging.info('Started')
    page_load(args.url, args.output)
    logging.info('Finished')


if __name__ == "__main__":
    main()
