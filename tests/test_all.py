import os
import subprocess
import tempfile

import pytest

from page_loader.app import KnownError, page_load
from tests import test_parametrize


URL = 'https://hexlet.io/courses'


@pytest.fixture()
def tmpdir_():
    path = os.path.abspath("./")
    with tempfile.TemporaryDirectory(dir=path) as dir_:
        yield dir_


def test_download(tmpdir_):
    page_load(URL, tmpdir_)
    dir_files = os.listdir(tmpdir_)
    assert 'hexlet-io-courses.html' in dir_files


def test_resource_dir_creating(tmpdir_):
    page_load(URL, tmpdir_)
    files_dir = f"{tmpdir_}/hexlet-io-courses_files"
    assert os.path.exists(files_dir)


@pytest.mark.parametrize('url,exp_name',
                         test_parametrize.urls_and_exp_names,
                         ids=test_parametrize.urls_and_exp_names_ids)
def test_different_ways_written_url(tmpdir_, url, exp_name):
    page_load(url, tmpdir_)
    dir_files = os.listdir(tmpdir_)
    assert dir_files != []
    assert exp_name in dir_files


def test_update_links(tmpdir_):
    page_load("https://git-scm.com/book/en/v2/Getting-Started-Installing-Git",
              tmpdir_)
    files_dir = f"{tmpdir_}/git-scm-com-book-en-v2-Getting" \
                f"-Started-Installing-Git_files"
    resources = os.listdir(files_dir)
    assert set(resources) == set(test_parametrize.exp_res_links)


@pytest.mark.parametrize('input', test_parametrize.urls_with_errors,
                         ids = test_parametrize.urls_with_errors_ids)
def test_http_error_handling(tmpdir_, input):
    with pytest.raises(KnownError):
        page_load(input, tmpdir_)


def test_no_permission_dir(tmpdir_):
    subprocess.call(['chmod', '0444', tmpdir_])
    with pytest.raises(KnownError):
        page_load(URL, tmpdir_)
