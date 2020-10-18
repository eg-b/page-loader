import os
import shutil
import string
from urllib.parse import urlparse

import requests
from bs4 import BeautifulSoup
from progress.bar import Bar

from page_loader.log import logger


CURRENT_DIR = os.getcwd()
PAGE = 'page'
PAGE_ELEMENT = 'page_item'
DIR = 'dir'
LOCAL_LINK = 'local_link'


class KnownError(Exception):
    pass


bar = Bar('Processing', max=5, suffix='%(percent)d%%')


def page_load(url, dir_path=CURRENT_DIR):
    if dir_path == CURRENT_DIR:
        logger.warning("No path specified, "
                       "the current directory will be used")
    if dir_path.endswith('/'):
        dir_path = dir_path[:-1]
    url_parts = urlparse(url, scheme='https')
    scheme = f"{url_parts.scheme}://"
    address = f"{url_parts.netloc}{url_parts.path}"
    url = f"{scheme}{address}"
    logger.debug(f"normalize url to {url}")
    logger.info(f"downloading page {url}")
    page = requests.get(url)
    name = f"{dir_path}/{get_name(url, type=PAGE)}"
    with open(name, "w") as file:
        try:
            file.write(page.text)
        except OSError as e:
            logger.error(e)
            raise KnownError() from e
    bar.next()
    storage_path = f"{dir_path}/{get_name(url, type=DIR)}"
    try:
        if os.path.exists(storage_path):
            logger.warning(f"directory {storage_path} already exists")
            logger.warning("clear to create a new one")
            shutil.rmtree(storage_path)
        logger.info(f"creating directory {storage_path}")
        os.makedirs(storage_path)
    except PermissionError as e:
        logger.debug(e)
        logger.error("You don't have enough privileges to save "
                     "to the selected directory. "
                     "Check permissions or try another one.")
        raise KnownError() from e
    logger.info(f"downloading page elements from {url}")
    get_resources(source=name, domain=url_parts.netloc, path=storage_path)
    bar.next()
    bar.finish()


def fetch_item(url, path=CURRENT_DIR):
    save_path = f"{os.path.abspath(path)}"
    try:
        res = requests.get(url)
    except (ConnectionError, requests.exceptions.ConnectionError) as e:
        logger.debug(e)
        logger.error("Connection error. "
                     "Check your network connection "
                     "or contact your administrator.")
        raise KnownError() from e
    except requests.exceptions.RequestException as e:
        logger.debug(e)
        logger.error(f"Request error while trying "
                     f"to download {url}. "
                     f"Check if the request is correct.")
        raise KnownError() from e
    name = f"{save_path}/{get_name(url, type=PAGE_ELEMENT)}"
    if os.path.exists(name):
        logger.warning("File already exists and will be overwritten")
    logger.debug(f"Writing downloaded item as {name}")
    with open(name, "w") as file:
        try:
            file.write(res.text)
        except OSError as e:
            logger.error(e)
            raise KnownError() from e
    return name


def get_resources(source, domain, path):
    with open(source) as file:
        soup = BeautifulSoup(file, 'html.parser')
        items = soup.find_all(['link', 'script', 'img'])
        for item in items:
            href = item.get('href')
            src = item.get('src')
            resource = src if src else href
            if resource:
                if '//' not in resource:
                    resource = resource[1:] if resource.startswith("/") \
                        else resource
                    logger.debug(f'downloading "{resource}" to "{path}"')
                    link = fetch_item(f"https://{domain}/{resource}", path)
                    item['src'] = link
                    logger.debug(f'link in page file has been '
                                 f'changed from "{resource}" '
                                 f'to "{link}"')
            bar.next()
    html = soup.prettify(soup.original_encoding)
    with open(source, 'w') as file:
        logger.info("rewriting page file with local links")
        file.write(html)


def get_name(item, type):
    path, ext = os.path.splitext(item)
    if len(ext) > 4:
        path = f"{path}{ext}"
        ext = ""
    schema, url = path.split('//')
    url = url[:-1] if url.endswith('/') else url
    name = ''.join(['-' if i in string.punctuation else i for i in url])
    if type == DIR:
        return f"{name}_files"
    elif type == PAGE:
        return f"{name}.html"
    elif type == PAGE_ELEMENT:
        name = f'{name}{ext}'
        if len(name) > 255:
            logger.warning("file name is too long, "
                           "it will be shortened due to OS restrictions")
        return name[:255]
