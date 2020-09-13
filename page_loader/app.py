import logging
import os
import requests
import string
import shutil
import sys
from urllib.parse import urlparse
from bs4 import BeautifulSoup


CURRENT_DIR = os.getcwd()
PAGE = 'page'
PAGE_ELEMENT = 'page_item'
DIR = 'dir'
LOCAL_LINK = 'local_link'


def page_load(url, path=CURRENT_DIR):
    if path == CURRENT_DIR:
        logging.warning("No path specified, "
                        "the current directory will be used")
    url_parts = urlparse(url, scheme='http')
    scheme = f"{url_parts.scheme}://"
    address = f"{url_parts.netloc}{url_parts.path}"
    url = f"{scheme}{address}"
    logging.debug(f"normalize url to {url}")
    storage_path = f"{path}/{get_name(url, type=DIR)}"
    try:
        if os.path.exists(storage_path):
            logging.warning(f"directory {storage_path} already exists")
            logging.warning("clear to create a new one")
            shutil.rmtree(storage_path)
        logging.info(f"creating directory {storage_path}")
        os.makedirs(storage_path)
    except PermissionError as e:
        logging.error(f"{e}")
        sys.exit(1)
    logging.info(f"downloading page {url}")
    page = download(url=f"{scheme}{address}", path=path)
    logging.info(f"downloading page elements from {url}")
    get_resources(source=page, path=storage_path)


def download(url, path=CURRENT_DIR, type=PAGE):
    save_path = f"{os.path.abspath(path)}"
    try:
        res = requests.get(url)
    except requests.exceptions.ConnectionError as e:
        logging.critical(f"{e}")
        sys.exit(1)
    name = f"{save_path}/{get_name(url, type)}"
    if os.path.exists(name):
        logging.warning("file already exists and will be overwritten")
    logging.debug(f"writing downloaded item as {name}")
    with open(name, "w") as file:
        file.write(res.text)
    return name


def get_resources(source, path):
    with open(source) as file:
        soup = BeautifulSoup(file, 'html.parser')
        for t in ['link', 'script', 'img']:
            for tag in soup.find_all(t):
                resource = tag.get('src')
                if resource:
                    logging.debug(f"downloading {resource} to {path}")
                    link = download(resource, path, type=PAGE_ELEMENT)
                    _, file = link.split(f'{path}/')
                    tag['src'] = f"{path}/{get_name(file, type=LOCAL_LINK)}"
                    logging.debug(f"link {resource} in page file has been "
                                  f"changed to {tag['src']}")
    html = soup.prettify(soup.original_encoding)
    with open(source, 'w') as file:
        logging.info("rewriting page file with local links")
        file.write(html)


def get_name(item, type):
    name, ext = os.path.splitext(item)
    if type == LOCAL_LINK:
        name = ''.join(['-' if i in string.punctuation else i for i in name])
        return f'{name}{ext}'
    else:
        url = name
        schema, url = url.split('//')
        url = url[:-1] if url.endswith('/') else url
        url = ''.join(['-' if i in string.punctuation else i for i in url])
        if type == DIR:
            return f"{url}_files"
        elif type == PAGE:
            return f"{url}.html"
        elif type == PAGE_ELEMENT:
            name = ''.join(['-' if i in string.punctuation
                            else i for i in url])
            return f'{name}{ext}' if ext else f'{name}'
