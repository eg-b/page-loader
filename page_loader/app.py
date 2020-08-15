import requests
import os
import string
import shutil
from urllib.parse import urlparse
from bs4 import BeautifulSoup


CURRENT_DIR = os.getcwd()
PAGE = 'page'
PAGE_ELEMENT = 'page_item'
DIR = 'dir'
URL = 'https://hexlet.io/courses'


def page_load(url, path=CURRENT_DIR):
    url_parts = urlparse(url, scheme='http')
    scheme = f"{url_parts.scheme}://"
    address = f"{url_parts.netloc}{url_parts.path}"
    url = f"{scheme}{address}"
    name = get_name(url, type=DIR)
    storage_path = f"{path}/{name}"
    if os.path.exists(storage_path):
        shutil.rmtree(storage_path)
    os.makedirs(storage_path)
    res = download(url=f"{scheme}{address}", path=path)
    get_resources(content=res.content,
                  path=storage_path)


def download(url, path=CURRENT_DIR, type=PAGE):
    save_path = f"{os.path.abspath(path)}"
    res = requests.get(url)
    name = get_name(url, type)
    with open(f"{save_path}/{name}", "w") as page_file:
        page_file.write(res.text)
    return res


def get_resources(content, path):
    page = BeautifulSoup(content, 'html.parser')
    for tag in ['link', 'script', 'img']:
        for item in page.find_all(tag):
            resource = item.get('src')
            if resource:
                download(resource, path, type=PAGE_ELEMENT)


def get_name(url, type):
    item, ext = os.path.splitext(url)
    schema, item_ = item.split('//')
    item_ = item_[:-1] if item_.endswith('/') else item_
    item_ = ''.join(['-' if i in string.punctuation else i for i in item_])
    if type == DIR:
        return f"{item_}_files"
    elif type == PAGE:
        return f"{item_}.html"
    elif type == PAGE_ELEMENT:
        name = ''.join(['-' if i in string.punctuation else i for i in item_])
        return f'{name}{ext}' if ext else f'{name}'