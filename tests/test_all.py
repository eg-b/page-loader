from page_loader.app import download
from tests import input_data
import pytest
import os

class TestLoadPage:

    @pytest.mark.parametrize('url,exp_name',
                             input_data.urls_and_exp_names,
                             ids=input_data.urls_and_exp_names_ids)
    def test_download(self, tmpdir, url, exp_name):
        dir = tmpdir.mkdir("test")
        download(url, dir)
        files = os.listdir(dir)
        assert files != []
        assert files[0] == exp_name

