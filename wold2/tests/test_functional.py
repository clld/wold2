from path import path

from clld.tests.util import TestWithApp

import wold2


class Tests(TestWithApp):
    __cfg__ = path(wold2.__file__).dirname().joinpath('..', 'development.ini').abspath()
    __setup_db__ = False

    def test_home(self):
        self.app.get('/', status=200)
        self.app.get('/terms', status=200)
        self.app.get('/semanticfield', status=200)
        self.app.get('/semanticfield/1', status=200)

    def test_values(self):
        self.app.get('/values?sEcho=1&parameter=1-1', xhr=True, status=200)
        self.app.get('/values?sEcho=1&contribution=15&iSortingCols=1&iSortCol_0=1', xhr=True, status=200)

    def test_parameters(self):
        self.app.get('/meaning', status=200)
        self.app.get('/meaning/1-1', status=200)
        self.app.get('/meaning/1-1.geojson', status=200)

    def test_languages(self):
        self.app.get('/language', status=200)
        self.app.get('/language.geojson', status=200)
        self.app.get('/language/13', status=200)

    def test_words(self):
        self.app.get('/word/72141423147775096', status=200)
