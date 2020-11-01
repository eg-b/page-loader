import time
import logging
import os
import string
from urllib.parse import urlparse

import requests
from bs4 import BeautifulSoup

from page_loader import cli


PAGE = 'page'
PAGE_ELEMENT = 'page_item'
DIR = 'dir'


class KnownError(Exception):
    pass


def page_load(url, dir_path=None, force=False):
    if not dir_path:
        logging.warning("No path specified, "
                       "the current directory will be used")
        dir_path = os.getcwd()
    if dir_path.endswith('/'):
        dir_path = dir_path[:-1]
    url_parts = urlparse(url, scheme='https')
    scheme = f"{url_parts.scheme}://"
    address = f"{url_parts.netloc}{url_parts.path}"
    url = f"{scheme}{address}"
    logging.info(f"downloading page {url}")
    page = get_content(url)
    page_file = get_name(url, type=PAGE)
    files_dir = get_name(url, type=DIR)
    page_file = f"{dir_path}/{page_file}"
    files_dir = f"{dir_path}/{files_dir}"
    if not os.path.exists(files_dir):
        logging.info(f"creating directory {files_dir}")
        try:
            os.makedirs(files_dir)
        except PermissionError as e:
            raise KnownError("You don't have enough privileges. "
                         "Check permissions or try another one.") from e
        except OSError as e:
            raise KnownError(e) from e
    else:
        if force:
            logging.warning(f"Directory {files_dir} already exists, "
                            f"files will be overwritten")
        else:
            raise KnownError(f"Directory {files_dir} already exists, "
                             f"clear the old one or try to use '-f' option")
    logging.info(f"downloading page elements from {url}")
    soup, page_items = prepare_resources(source=page, domain=url_parts.netloc,
                                         files_path=files_dir)
    html = soup.prettify(soup.original_encoding)
    write_to_file(file_name=page_file, source=html)
    max_bar = 1 if len(page_items) == 0 else len(page_items) + 1
    bar = cli.setup_bar(max=max_bar)
    for item in page_items:
        link, new_name = item
        content = get_content(link)
        write_to_file(new_name, content)
        bar.next()
    bar.next()
    bar.finish()


def prepare_resources(source, domain, files_path):
    soup = BeautifulSoup(source, 'html.parser')
    items = soup.find_all(['link', 'script', 'img'])
    page_items = []
    for item in items:
        href = item.get('href')
        src = item.get('src')
        resource = src if src else href
        if resource:
            if domain not in resource and '//' not in resource:
                resource = resource[1:] if resource.startswith("/") \
                    else resource
                link = f'https://{domain}/{resource}'
                file_name = get_name(item=link, type=PAGE_ELEMENT)
                element = (link, file_name)
                page_items.append(element)
                item['src'] = f"{files_path}/{file_name}"
    return soup, page_items


def get_name(item, type, dir=None):
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
        max_len = os.pathconf('/', 'PC_NAME_MAX')
        if len(f'{name}{ext}') > max_len:
            logging.warning("file name is too long, "
                           "it will be shortened due to OS restrictions")
        name = f'{name[:max_len - len(ext)]}'
        name_with_ext = f"{name}{ext}"
        if name_with_ext in os.listdir(dir):
            name = f'{name[:max_len - (len(ext) + 6)]}'
            mark = str(time.time())[-6:]
            name_with_ext = f"{name}{mark}{ext}"
        return name_with_ext



def get_content(url):
    try:
        res = requests.get(url)
        res.raise_for_status()
    except requests.exceptions.HTTPError as e:
        raise KnownError(e) from e
    except (ConnectionError, requests.exceptions.ConnectionError) as e:
        raise KnownError("Connection error. "
                     "Check your network connection "
                     "or contact your administrator.") from e
    except requests.exceptions.RequestException as e:
        raise KnownError(f"Request error while trying "
                         f"to download {url}. "
                         f"Check if the request is correct.") from e
    if 'text' in res.headers['Content-Type']:
        return res.text
    else:
        return res.content


def write_to_file(file_name, source):
    mode = "wb" if isinstance(source, bytes) else "w"
    try:
        with open(file_name, mode) as file:
            file.write(source)
    except PermissionError as e:
        raise KnownError("You don't have enough privileges. "
                     "Check permissions or try another one.") from e
    except OSError as e:
        raise KnownError(e) from e
