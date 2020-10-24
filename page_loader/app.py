import os
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


class KnownError(Exception):
    pass


bar = Bar('Processing ', max=4, suffix='%(percent)d%%')


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
    page = get(url)
    name = f"{dir_path}/{get_name(url, type=PAGE)}"
    write_to_file(file_name=name, source=page.content)
    bar.next()
    files_storage_path = f"{dir_path}/{get_name(url, type=DIR)}"
    if not os.path.exists(files_storage_path):
        logger.info(f"creating directory {files_storage_path}")
        try:
            os.makedirs(files_storage_path)
        except PermissionError:
            logger.error("You don't have enough privileges. "
                         "Check permissions or try another one.")
        except OSError as e:
            logger.error(e)
    else:
        logger.warning(f"directory {files_storage_path} already exists."
                       f" Files will be rewritten")
    logger.info(f"downloading page elements from {url}")
    bar.next()
    update_links(source=name, domain=url_parts.netloc,
                 path=files_storage_path)
    bar.finish()


def update_links(source, domain, path):
    with open(source) as file:
        soup = BeautifulSoup(file, 'html.parser')
        items = soup.find_all(['link', 'script', 'img'])
        for item in items:
            href = item.get('href')
            src = item.get('src')
            resource = src if src else href
            if resource:
                if domain not in resource and '//' not in resource:
                    resource = resource[1:] if resource.startswith("/") \
                        else resource
                    logger.debug(f'downloading "{resource}" to "{path}"')
                    link = f'https://{domain}/{resource}'
                    file_name = get_name(item=link, type=PAGE_ELEMENT)
                    file = f"{path}/{file_name}"
                    res = get(link)
                    if os.path.exists(file):
                        logger.warning("File already exists "
                                       "and will be overwritten")
                    logger.debug(f"Writing downloaded item as {file_name}")
                    write_to_file(file, res.content)
                    item['src'] = file
                    logger.debug(f'link in page file has been '
                                 f'changed from "{resource}" '
                                 f'to "{file}"')
    bar.next()
    html = soup.prettify(soup.original_encoding)
    logger.info("rewriting page file with local links")
    write_to_file(source, html, bytes=False)
    bar.next()


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
        if len(f'{name}{ext}') > 255:
            logger.warning("file name is too long, "
                           "it will be shortened due to OS restrictions")
        return f'{name[:255 - len(ext)]}{ext}'


def get(url):
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
    try:
        res.raise_for_status()
    except requests.exceptions.HTTPError as e:
        logger.error(e)
        raise KnownError() from e
    return res


def write_to_file(file_name, source, bytes=True):
    try:
        mode = "wb" if bytes else "w"
        with open(file_name, mode) as file:
            file.write(source)
    except PermissionError as e:
        logger.debug(e)
        logger.error("You don't have enough privileges. "
                     "Check permissions or try another one.")
        raise KnownError() from e
    except OSError as e:
        logger.error(e)
        raise KnownError() from e
