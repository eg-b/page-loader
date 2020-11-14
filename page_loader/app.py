import logging
import os
import string
from progress.bar import Bar
from urllib.parse import urlparse

import requests
from bs4 import BeautifulSoup


PAGE = 'page'
PAGE_ELEMENT = 'page_item'
DIR = 'dir'


class KnownError(Exception):
    pass


def setup_bar(max):
    logging.debug(f"setup bar with max value: {max}")
    return Bar('Processing ', max=max, suffix='%(percent)d%%')


def page_load(url, dir_path=None, force=False):
    logging.debug(f'page_load function get arguments: '
                  f'url - {url}, dir_path - {dir_path}, '
                  f'force - {force}')
    if dir_path is None:
        logging.warning("No path specified, "
                        "the current directory will be used")
        dir_path = os.getcwd()
    dir_path = dir_path.rstrip('/')
    url_parts = urlparse(url, scheme='https')
    scheme = f"{url_parts.scheme}://"
    domain = url_parts.netloc
    url = f"{scheme}{url_parts.netloc}{url_parts.path}"
    logging.info(f"downloading page {url}")
    page = download_content(url)
    page_file = get_name(url, type=PAGE)
    page_file = f"{dir_path}/{page_file}"
    files_dir = get_name(url, type=DIR)
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
    html, page_items = prepare_resources(source=page, domain=domain,
                                         files_path=files_dir)
    write_to_file(file_path=page_file, source=html)
    max_bar = 1 if len(page_items) == 0 else len(page_items)
    bar = setup_bar(max=max_bar)
    logging.info(f"downloading page elements from {url}")
    for item in page_items:
        link, new_name = item
        try:
            content = download_content(link)
        except KnownError as e:
            logging.warning(f"Can't load item {link}. {e}")
            continue
        item_path = f"{files_dir}/{new_name}"
        write_to_file(file_path=item_path, source=content)
        bar.next()
    bar.next()
    bar.finish()


def prepare_resources(source, domain, files_path):
    logging.debug(f'prepare_resources function got arguments: '
                  f'domain - {domain}, '
                  f'files_path - {files_path}')
    soup = BeautifulSoup(source, 'html.parser')
    items = soup.find_all(['link', 'script', 'img'])
    page_items = []
    for item in items:
        href = item.get('href')
        src = item.get('src')
        resource = src if src else href
        if resource:
            if domain not in resource and '//' not in resource:
                domain = domain.rstrip('/')
                resource = resource.lstrip('/')
                link = f'https://{domain}/{resource}'
                file_name = get_name(item=link, type=PAGE_ELEMENT)
                element = (link, file_name)
                page_items.append(element)
                item['src'] = f"{files_path}/{file_name}"
    logging.debug(f"return elements: {page_items}")
    page = soup.prettify(soup.original_encoding)
    return page, page_items


def get_name(item, type, dir=None):
    logging.debug(f'get_name function got arguments: '
                  f'item - {item}, type - {type}, '
                  f'dir - {dir}')
    if type == PAGE_ELEMENT:
        file, ext = os.path.splitext(item)
        if len(ext) > 5:
            file = f"{file}{ext}"
            ext = ""
        schema, url = file.split('//')
    else:
        schema, url = item.split('//')
    url = url.rstrip('/')
    new_name = ''.join(['-' if i in string.punctuation else i for i in url])
    if type == DIR:
        result = f"{new_name}_files"
    elif type == PAGE:
        result = f"{new_name}.html"
    elif type == PAGE_ELEMENT:
        max_len = os.pathconf('/', 'PC_NAME_MAX')
        if len(f'{new_name}{ext}') > max_len:
            logging.debug(f"max path length is {max_len}")
            logging.warning("file name is too long, "
                            "it will be shortened due to OS restrictions")
            new_name = f'{new_name[:max_len - len(ext)]}'
        name_with_ext = f"{new_name}{ext}"
        files_dir = os.listdir(dir)
        if name_with_ext in files_dir:
            while name_with_ext in files_dir:
                counter = 1
                mark = f"_{counter}"
                new_name = f'{new_name[:max_len - (len(ext) + len(mark))]}'
                name_with_ext = f"{new_name}{mark}{ext}"
                counter += 1
        result = name_with_ext
    logging.debug(f"return new name {result}")
    return result


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
        raise KnownError(f"Request error while trying "
                         f"to download {url}. "
                         f"Check if the request is correct.") from e
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
