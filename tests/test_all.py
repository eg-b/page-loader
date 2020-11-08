import os
import subprocess
import tempfile

import pytest
import requests_mock

from page_loader.app import KnownError, page_load
from page_loader import app
from tests import test_parametrize as params


GH_URL = "https://eg-b.github.io/python-project-lvl3/"
TEST_URL = "http://test.io/test"


@pytest.fixture()
def tmpdir_():
    path = os.path.abspath("./")
    with tempfile.TemporaryDirectory(dir=path) as dir_:
        yield dir_


@pytest.fixture()
def mock():
    with requests_mock.Mocker(real_http=True) as m:
        yield m


@pytest.mark.parametrize("item,type,exp_result",
                         params.NAMES,
                         ids=["page name",
                              "page item name",
                              "files directory name",
                              "over max len page item name"])
def test_get_name(item, type, exp_result):
    new_name = app.get_name(item, type)
    assert new_name == exp_result, 'incorrect new name'


def test_names_match_after_truncation(tmpdir_):
    name = 'test-script'.ljust(params.max_len - 4, '0') + '.ext'
    file = f"{tmpdir_}/{name}"
    with open(file, 'w') as f:
        f.close()
    new_name = app.get_name(item=params.max_len_link,
                            type=app.PAGE_ELEMENT,
                            dir=tmpdir_)
    assert new_name != name, "names must not match"
    new_name, ext = os.path.splitext(new_name)
    assert new_name.endswith('_1'), "incorrect new name"


def test_prepare_page_elements(tmpdir_):
    html = os.path.abspath("../docs/index.html")
    with open(html, 'r') as file:
        page, items = app.prepare_resources(
            source=file, domain="eg-b.github.io",
            files_path=tmpdir_)
        assert items == params.PAGE_ELEMENTS,\
            "unexpected page elements"
        for i in items:
            link, name = i
            assert f"{tmpdir_}/{name}" in page, \
                "the page should have such a link"


@pytest.mark.parametrize('url,exp_name',
                         params.URLS_AND_EXP_NAMES,
                         ids=['scheme + hostname + path',
                              'hostname + path'])
def test_different_ways_written_url(tmpdir_, url, exp_name):
    page_load(url, tmpdir_)
    dir_files = os.listdir(tmpdir_)
    assert dir_files != [], "there is no page"
    assert exp_name in dir_files, "unexpected name"


@pytest.mark.parametrize('status_code', params.ERROR_CODES,
                         ids=params.ERROR_CODES_IDS)
def test_http_error_handling(mock, status_code):
    mock.get(TEST_URL, text='data', status_code=status_code)
    with pytest.raises(KnownError):
        app.download_content(input)


def test_item_load_fail(mock, tmpdir_):
    for item in params.PAGE_ELEMENTS_WITH_CODES:
        link, status_code = item
        mock.get(link, text='data', headers={'Content-Type': 'text'},
                 status_code=status_code)
    app.page_load(GH_URL, dir_path=tmpdir_, force=True)
    dir = os.listdir(tmpdir_)
    print(dir)
    exp_name = "eg-b-github-io-python-project-lvl3"
    assert f"{exp_name}.html" in dir
    files_dir_name = f"{exp_name}_files"
    assert files_dir_name in dir
    assert len(os.listdir(f"{tmpdir_}/{files_dir_name}")) == 2


def test_no_permission_dir(tmpdir_):
    subprocess.call(['chmod', '0444', tmpdir_])
    with pytest.raises(KnownError):
        page_load(GH_URL, tmpdir_)


def test_page_load(tmpdir_, mock):
    URL = 'http://test.io/test'
    mock.get(URL, text='data', headers={'Content-Type': 'text'})
    files_dir = "test-io-test_files"
    page_load(URL, dir_path=tmpdir_, force=True)
    tmpdir_files = os.listdir(tmpdir_)
    assert 'test-io-test.html' in tmpdir_files, "unexpected name"
    assert files_dir in tmpdir_files, "there is no _files directory"
