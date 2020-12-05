import os

from page_loader import app

max_len = os.pathconf('/', 'PC_NAME_MAX')


NAMES = [
    ('http://test.io/courses', app.get_name, 'test-io-courses'),
    ('http://test.io/courses', app.get_directory_name, 'test-io-courses_files'),
    ('http://test.io/courses', app.get_page_name, 'test-io-courses.html')
]

PAGE_ELEMENTS_NAMES = [
    ('http://test.io/courses', 'assets/pic.png', 'test-io-assets-pic.png'),
    ('http://test.io', 'assets/pic.png', 'test-io-assets-pic.png'),
    ('http://test.io', 'assets/pic', 'test-io-assets-pic')
]

IS_LOCAL_TEST_ITEMS = [
    ("https://cdn2.test.io/assets/menu.css", 'test.io', False),
    ("https://test.io/assets/menu.css", 'test.io', True),
    ("assets/menu.css", 'test.io', True)
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


ERROR_CODES = ["400", "401", "403", "404", "500"]
ERROR_CODES_IDS = ["bad request", "unathorized", "no privileges",
                   "not found", "server error"]
