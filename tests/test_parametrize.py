from page_loader import app
import os


max_len = os.pathconf('/', 'PC_NAME_MAX')

max_len_link = 'http://test/script'.ljust(max_len + 7, '0') + '.ext'
max_len_expected_name = 'test-script'.ljust(max_len - 4, '0') + '.ext'


NAMES = [
    ('http://test.io/courses', app.PAGE, 'test-io-courses.html'),
    ('http://test.io/assets/test.css', app.PAGE_ELEMENT,
     'test-io-assets-test.css'),
    ('http://test.io', app.DIR, 'test-io_files'),
    (max_len_link, app.PAGE_ELEMENT, max_len_expected_name)
]


PAGE_ELEMENTS = [
    ('https://eg-b.github.io/python-project-lvl3/assets/application.css',
     'eg-b-github-io-python-project-lvl3-assets-application.css'),
    ('https://eg-b.github.io/python-project-lvl3/courses/hexlet',
     'eg-b-github-io-python-project-lvl3-courses-hexlet'),
    ('https://eg-b.github.io/python-project-lvl3/assets/professions'
     '/python.svg',
     'eg-b-github-io-python-project-lvl3-assets-professions-python.svg'),
    ('https://eg-b.github.io/python-project-lvl3/packs/js/runtime.js',
     'eg-b-github-io-python-project-lvl3-packs-js-runtime.js')]


PAGE_ELEMENTS_WITH_CODES = [
    ('https://eg-b.github.io/python-project-lvl3/assets/application.css', 404),
    ('https://eg-b.github.io/python-project-lvl3/courses/hexlet', 200),
    ('https://eg-b.github.io/python-project-lvl3/assets/professions'
     '/python.svg', 500),
    ('https://eg-b.github.io/python-project-lvl3/packs/js/runtime.js', 200)]


URLS_AND_EXP_NAMES = [
    ('https://eg-b.github.io/python-project-lvl3',
     'eg-b-github-io-python-project-lvl3.html'),
    ('eg-b.github.io/python-project-lvl3',
     'eg-b-github-io-python-project-lvl3.html')]


ERROR_CODES = ["400", "401", "403", "404", "500"]
ERROR_CODES_IDS = ["bad request", "unathorized", "no privileges",
                   "not found", "server error"]
