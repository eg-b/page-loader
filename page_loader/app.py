import logging
import os
import shutil
import string
from urllib.parse import urlparse, urlunparse

import requests
from bs4 import BeautifulSoup
from progress.bar import Bar


PAGE = 'page'
PAGE_ELEMENT = 'page_item'
DIR = 'dir'
LINK = 'link'
SCRIPT = 'script'
IMG = 'img'


class KnownError(Exception):
    pass


def download_page(url, output_directory=None, overwrite=False):
    logging.debug(f'\ndownload_page(\n'
                  f'url={url}\n'
                  f'dir_path={output_directory}\n'
                  f'overwrite={overwrite}')
    if output_directory is None:
        output_directory = os.getcwd()
    output_directory = output_directory.rstrip('/')
    page_file = get_page_name(url)
    page_file = f"{output_directory}/{page_file}"
    files_dir = get_directory_name(url)
    files_dir = f"{output_directory}/{files_dir}"
    create_files_directory(dir_name=files_dir, overwrite=overwrite)
    page_items = download_single_page(url=url,
                                      page_name=page_file,
                                      files_dir=files_dir)
    max_bar = 1 if len(page_items) == 0 else len(page_items)
    with Bar('Processing ', max=max_bar, suffix='%(percent)d%%') as bar:
        logging.info(f"downloading page elements from {url}")
        for link, new_name in page_items:
            bar.next()
            try:
                content = download_content(link)
            except KnownError as e:
                logging.warning(f"Can't load item {link}. {e}")
                continue
            item_path = f"{files_dir}/{new_name}"
            write_to_file(file_path=item_path, source=content)
        bar.next()


def download_single_page(url, page_name, files_dir):
    logging.info(f"downloading page {url}")
    original_page = download_content(url)
    new_page, page_items = prepare_resources(source=original_page,
                                             url=url,
                                             files_path=files_dir)
    write_to_file(file_path=page_name, source=new_page)
    return page_items


def create_files_directory(dir_name, overwrite):
    if os.path.exists(dir_name):
        if overwrite:
            logging.warning(f"Directory {dir_name} already exists, "
                            f"files will be overwritten")
            shutil.rmtree(dir_name)
        else:
            raise KnownError(f"Directory {dir_name} already exists, "
                             f"clear the old one or try to use '-f' option")
    logging.info(f"creating directory {dir_name}")
    try:
        os.makedirs(dir_name)
    except PermissionError as e:
        raise KnownError("You don't have enough privileges. "
                         "Check permissions or try another one.") from e
    except OSError as e:
        raise KnownError(e) from e


def prepare_resources(source, url, files_path):
    logging.debug(f'\nprepare_resources(\n'
                  f'url={url}\n'
                  f'files_path={files_path}')
    url_parts = urlparse(url, scheme='https')
    soup = BeautifulSoup(source, 'html.parser')
    items = soup.find_all([LINK, SCRIPT, IMG])
    page_items = []
    for item in items:
        if item.name in [SCRIPT, IMG]:
            resource = item.get('src')
        elif item.name == LINK:
            resource = item.get('href')
        if resource and is_local(item=resource, domain=url_parts.netloc):
            resource = resource.lstrip('/')
            file_name = get_page_element_name(
                item=resource, url=url)
            link = urlunparse((url_parts.scheme, url_parts.netloc,
                               f"/{resource}", "", "", ""))
            element = (link, file_name)
            page_items.append(element)
            item['src'] = f"{files_path}/{file_name}"
    logging.debug(f"return elements: {page_items}")
    page = soup.prettify(soup.original_encoding)
    return page, page_items


def is_local(item, domain):
    item_parts = urlparse(item)
    item_domain = item_parts.netloc
    if item_domain:
        if item_domain == domain:
            return True
        else:
            return False
    if item_parts.path:
        return True
    else:
        False


def get_directory_name(item):
    logging.debug(f'\nget_directory_name(\n'
                  f'item={item}')
    name = get_name(item)
    return f"{name}_files"


def get_page_name(item):
    logging.debug(f'\nget_page_name(\n'
                  f'item={item}')
    name = get_name(item)
    return f"{name}.html"


def get_page_element_name(item, url):
    logging.debug(f'\nget_page_element_name(\n'
                  f'item={item}')
    url_parts = urlparse(url)
    if url_parts.path:
        url, _ = url.split(url_parts.path)
    item = f"{url}/{item}"
    file, ext = os.path.splitext(item)
    if len(ext) > 5:
        name = get_name(item)
        ext = ""
    else:
        name = get_name(file)
    return f"{name}{ext}"


def get_name(item):
    logging.debug(f'\nget_name(\n'
                  f'item={item}')
    url_parts = urlparse(item)
    if url_parts.scheme:
        _, item = item.split(f"{url_parts.scheme}://")
    item = item.rstrip('/')
    name = ''.join(['-' if i in string.punctuation else i for i in item])
    logging.debug(f"return new name {name}")
    return name


def download_content(url):
    logging.debug(f'get_content function got arguments: url - {url}')
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
        raise KnownError(
            f"Request error while trying to download {url}. "
            "Check if the request is correct.") from e
    logging.debug("successfully loaded")
    if 'text' in res.headers['Content-Type']:
        return res.text
    else:
        return res.content


def write_to_file(file_path, source):
    mode = "wb" if isinstance(source, bytes) else "w"
    try:
        with open(file_path, mode) as file:
            file.write(source)
    except PermissionError as e:
        raise KnownError("You don't have enough privileges. "
                         "Check permissions or try another one.") from e
    except OSError as e:
        raise KnownError(e) from e
