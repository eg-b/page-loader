![Python application](https://github.com/eg-b/python-project-lvl3/workflows/Python%20application/badge.svg)
[![Maintainability](https://api.codeclimate.com/v1/badges/c42c04985953eca93933/maintainability)](https://codeclimate.com/github/eg-b/python-project-lvl3/maintainability)
<a href="https://codeclimate.com/github/eg-b/python-project-lvl3/test_coverage"><img src="https://api.codeclimate.com/v1/badges/c42c04985953eca93933/test_coverage" /></a>

### Usage

```sh
usage: page-loader [-h] [--output= DIR] [--log= LEVEL] url

positional arguments:
  url            web address

optional arguments:
  -h, --help     show this help message and exit
  --output= DIR  set download directory
  --log= LEVEL   set the logging level: debug, warning, info
```
Example:
```sh
$ page-loader --output=/user/home/ --log=INFO https://hexlet.ru/courses
```

### Installation

```sh
$ python3 -m pip install --user -i https://test.pypi.org/simple/ --extra-index-url https://pypi.org/simple/ eg-b_page_loader
```

[![asciicast](https://asciinema.org/a/CNZN07MPVKyc1cBFCdnG8tr10.svg)](https://asciinema.org/a/CNZN07MPVKyc1cBFCdnG8tr10)


### Page download
[![asciicast](https://asciinema.org/a/yUpXwX5PLDA8oLY950Zyd1nkx.svg)](https://asciinema.org/a/yUpXwX5PLDA8oLY950Zyd1nkx)

### Page download errors
[![asciicast](https://asciinema.org/a/Le1AYL0fafNAW6P8rw9IRkVqo.svg)](https://asciinema.org/a/Le1AYL0fafNAW6P8rw9IRkVqo)