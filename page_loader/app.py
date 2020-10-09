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
    storage_path = f"{dir_path}/{get_name(url, type=DIR)}"
    try:
        if os.path.exists(storage_path):
            logger.warning(f"directory {storage_path} already exists")
            logger.warning("clear to create a new one")
            shutil.rmtree(storage_path)
        logger.info(f"creating directory {storage_path}")
        os.makedirs(storage_path)
    except PermissionError as e:
        logger.debug(f"{e}")
        logger.error("You don't have enough privileges to save "
                     "to the selected directory. "
                     "Check permissions or try another one.")
        raise KnownError() from e
    logger.info(f"downloading page {url}")
    page = download(url=f"{scheme}{address}", path=dir_path)
    bar.next()
    logger.info(f"downloading page elements from {url}")
    get_resources(source=page, domain=url_parts.netloc, path=storage_path)
    bar.next()
    bar.finish()


def download(url, path=CURRENT_DIR, type=PAGE):
    save_path = f"{os.path.abspath(path)}"
    try:
        res = requests.get(url)
    except (ConnectionError, requests.exceptions.ConnectionError) as e:
        logger.debug(f"{e}")
        logger.error("Connection error. "
                     "Check your network connection "
                     "or contact your administrator.")
        raise KnownError() from e
    except requests.exceptions.RequestException as e:
        logger.debug(f"{e}")
        logger.error(f"Request error while trying "
                     f"to download {url}. "
                     f"Check if the request is correct.")
        raise KnownError() from e
    name = f"{save_path}/{get_name(url, type)}"
    if os.path.exists(name):
        logger.warning("File already exists and will be overwritten")
    logger.debug(f"Writing downloaded item as {name}")
    with open(name, "w") as file:
        try:
            file.write(res.text)
        except OSError:
            logger.warning("file name is too long, "
                           "it will be shortened due to OS restrictions")

    return name

def get_resources(source, domain, path):
    with open(source) as file:
        soup = BeautifulSoup(file, 'html.parser')
        for tag in ['link', 'script', 'img']:
            for item in soup.find_all(tag):
                if tag == 'link':
                    resource = item.get('href')
                elif tag in ['script', 'img']:
                    resource = item.get('src')
                if resource:
                    if domain not in resource and not '//' in resource:
                        logger.debug(f'downloading "{resource}" to "{path}"')
                        link = download(f"https://{domain}{resource}", path, type=PAGE_ELEMENT)
                        _, file = link.split(f'{path}/')
                        item['src'] = f'{path}/{get_name(file, type=LOCAL_LINK)}'
                        logger.debug(f'link in page file has been '
                                     f'changed from "{resource}" '
                                     f'to "{item["src"]}"')
            bar.next()
    html = soup.prettify(soup.original_encoding)
    with open(source, 'w') as file:
        logger.info("rewriting page file with local links")
        file.write(html)


def get_name(item, type):
    name, ext = os.path.splitext(item)
    if type == LOCAL_LINK:
        name = ''.join(['-' if i in string.punctuation else i for i in name])
        return f'{name}{ext}'
    else:
        schema, url = name.split('//')
        url = url[:-1] if url.endswith('/') else url
        url = ''.join(['-' if i in string.punctuation else i for i in url])
        if type == DIR:
            return f"{url}_files"
        elif type == PAGE:
            return f"{url}.html"
        elif type == PAGE_ELEMENT:
            name = ''.join(['-' if i in string.punctuation
                            else i for i in url])
            if ext:
                if len(f'{name}{ext}') > 255:
                    while len(f'{name}{ext}') > 255:
                        name = name[:-1]
                name = f'{name[:len(ext)]}{ext}'
            else:
                if len(name) > 255:
                    while len(name) > 255:
                        name = name[:-1]
            return name
