import requests
import os
import string
from urllib.parse import urlparse


CURRENT_DIR = os.getcwd()


def download(url, dir=CURRENT_DIR):
    save_path = f"{os.path.abspath(dir)}"
    url_parts = urlparse(url)
    scheme = "http://" if url_parts.scheme == '' else f"{url_parts.scheme}://"
    address = f"{url_parts.netloc}{url_parts.path}"
    filename = [i if i not in string.punctuation
                else '-' for i in address]
    filename = f"{save_path}/{''.join(filename)}.html"
    res = requests.get(f'{scheme}{address}')
    with open(filename, "w") as page_file:
        page_file.write(res.text)
    return
