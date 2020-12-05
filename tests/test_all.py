import os
import subprocess
import tempfile

import pytest
import requests_mock

from page_loader import app
from page_loader.app import KnownError, download_page
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


@pytest.mark.parametrize("item,func,exp_result",
                         params.NAMES,
                         ids=["name",
                              "directory name",
                              "page name"])
def test_get_name(item, func, exp_result):
    new_name = func(item)
    assert new_name == exp_result, 'incorrect new name'


@pytest.mark.parametrize("url,item,exp_result", params.PAGE_ELEMENTS_NAMES,
                         ids=['url with path',
                              'resourse with ext',
                              'resourse with no ext'])
def test_get_page_element_name(url, item, exp_result):
    new_name = app.get_page_element_name(item, url)
    assert new_name == exp_result, 'incorrect new name'


@pytest.mark.parametrize("item,domain,exp_result",
                         params.IS_LOCAL_TEST_ITEMS,
                         ids=['not local',
                              'local, full url',
                              'local, path only'])
def test_is_local(item, domain, exp_result):
    assert app.is_local(item=item, domain=domain) is exp_result



def test_prepare_page_elements(tmpdir_):
    html = os.path.abspath("docs/index.html")
    with open(html, 'r') as file:
        page, items = app.prepare_resources(
            source=file, url=GH_URL,
            files_path=tmpdir_)
        assert items == params.PAGE_ELEMENTS,\
            "unexpected page elements"
        for i in items:
            link, name = i
            assert f"{tmpdir_}/{name}" in page, \
                "new link was not found on the page"


@pytest.mark.parametrize('status_code', params.ERROR_CODES,
                         ids=params.ERROR_CODES_IDS)
def test_http_error_handling(mock, status_code):
    mock.get(TEST_URL, text='data', status_code=status_code)
    with pytest.raises(KnownError):
        app.download_content(input)


def test_write_file(tmpdir_):
    page = "page.html"
    with open(f"{tmpdir_}/{page}", 'w') as pg:
        pg.write("test")
    assert page in os.listdir(tmpdir_)


def test_write_file_over_max_len_name(tmpdir_):
    name = 'page.html'.ljust(params.max_len + 1, '0')
    with pytest.raises(OSError):
        with open(f"{tmpdir_}/{name}", 'w') as pg:
            pg.write("test")


def test_no_permission_dir(tmpdir_):
    subprocess.call(['chmod', '0444', tmpdir_])
    with pytest.raises(KnownError):
        app.write_to_file(f"{tmpdir_}/test", tmpdir_)


def test_page_load(tmpdir_, mock):
    URL = 'http://test.io/test'
    mock.get(URL, text='data', headers={'Content-Type': 'text'})
    files_dir = "test-io-test_files"
    download_page(URL, output_directory=tmpdir_, overwrite=True)
    tmpdir_files = os.listdir(tmpdir_)
    assert 'test-io-test.html' in tmpdir_files, "unexpected name"
    assert files_dir in tmpdir_files, "there is no _files directory"


def test_item_load_fail(mock, tmpdir_):
    for item in params.PAGE_ELEMENTS_WITH_CODES:
        link, status_code = item
        mock.get(link, text='data', headers={'Content-Type': 'text'},
                 status_code=status_code)
    app.download_page(GH_URL, output_directory=tmpdir_, overwrite=True)
    dir = os.listdir(tmpdir_)
    print(dir)
    exp_name = "eg-b-github-io-python-project-lvl3"
    assert f"{exp_name}.html" in dir
    files_dir_name = f"{exp_name}_files"
    assert files_dir_name in dir
    assert len(os.listdir(f"{tmpdir_}/{files_dir_name}")) == 2