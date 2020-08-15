#!/usr/bin/env python3
from page_loader.cli import parser
from page_loader.app import download


def main():
    args = parser.parse_args()
    download(args.url, args.output)


if __name__ == "__main__":
    main()
