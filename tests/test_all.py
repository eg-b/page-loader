import os
import subprocess
import tempfile

import pytest
from bs4 import BeautifulSoup

from page_loader.app import KnownError, fetch_item, page_load
from tests import input_data


URL = 'https://hexlet.io/courses'
URL2 = "https://ru.wikipedia.org/wiki/Ubuntu"


@pytest.fixture()
def tmpdir_():
    path = os.path.abspath("./")
    with tempfile.TemporaryDirectory(dir=path) as dir_:
        yield dir_


def test_download(tmpdir_):
    fetch_item(URL, tmpdir_)
    dir_files = os.listdir(tmpdir_)
    assert 'hexlet-io-courses.html' in dir_files


def test_resource_dir_creating(tmpdir_):
    page_load(URL, tmpdir_)
    dir_files = os.listdir(tmpdir_)
    assert 'hexlet-io-courses_files' in dir_files


@pytest.mark.parametrize('url,exp_name',
                         input_data.urls_and_exp_names,
                         ids=input_data.urls_and_exp_names_ids)
def test_different_ways_written_url(tmpdir_, url, exp_name):
    page_load(url, tmpdir_)
    dir_files = os.listdir(tmpdir_)
    assert dir_files != []
    assert exp_name in dir_files


def test_rewrite_links(tmpdir_):
    page_load(URL, tmpdir_)
    files_folder = f'{tmpdir_}/hexlet-io-courses_files'
    resources = os.listdir(files_folder)
    resources_links = [f"{files_folder}/{item}" for item in resources]
    html_links = []
    with open(f'{tmpdir_}/hexlet-io-courses.html') as file:
        soup = BeautifulSoup(file, 'html.parser')
        for t in ['link', 'script', 'img']:
            for tag in soup.find_all(t):
                link = tag.get('src')
                if link:
                    html_links.append(link)
    assert sorted(html_links) == sorted(resources_links)


def test_connection_error(tmpdir_):
    with pytest.raises(KnownError):
        page_load('https://hexqwert.io/courses', tmpdir_)


def test_no_permission_dir(tmpdir_):
    subprocess.call(['chmod', '0444', tmpdir_])
    with pytest.raises(KnownError):
        page_load(URL, tmpdir_)

def test_mint(tmpdir_):
    page_load(URL2, tmpdir_)
    assert True