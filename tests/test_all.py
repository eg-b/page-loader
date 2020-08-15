from page_loader.app import download, page_load
from tests import input_data
import pytest
import os
import tempfile


URL = 'https://hexlet.io/courses'


def test_download(tmpdir_):
    res = download(URL, tmpdir_)
    dir_files = os.listdir(tmpdir_)
    assert res.status_code == 200
    assert 'hexlet-io-courses.html' in dir_files


def test_resource_dir_creating(tmpdir_):
    page_load(URL, tmpdir_)
    dir_files = os.listdir(tmpdir_)
    assert 'hexlet-io-courses_files' in dir_files


@pytest.mark.parametrize('url,exp_name',
                         input_data.urls_and_exp_names,
                         ids=input_data.urls_and_exp_names_ids)
def test_different_ways_written_url(tmpdir_, url, exp_name):
    page_load(url=url, path=tmpdir_)
    dir_files = os.listdir(tmpdir_)
    assert dir_files != []
    assert exp_name in dir_files


def test_rewrite_links(tmpdir_):
    page_load(URL, tmpdir_)
    resources = os.listdir(f'{tmpdir_}/hexlet-io-courses_files')
    with open(f'{tmpdir_}/hexlet-io-courses.html') as page:
        soup = BeautifulSoup(content, 'html.parser')
        for item in resources:
            assert item in soup


@pytest.fixture()
def tmpdir_():
    path = os.path.abspath("./")
    with tempfile.TemporaryDirectory(dir=path) as fp:
        yield fp