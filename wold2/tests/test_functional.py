from path import path

from clld.tests.util import TestWithApp

import wold2


class Tests(TestWithApp):
    __cfg__ = path(wold2.__file__).dirname().joinpath('..', 'development.ini').abspath()
    __setup_db__ = False

    def test_home(self):
        self.app.get_html('/')
        self.app.get_html('/terms')
        self.app.get_html('/semanticfield')
        self.app.get_html('/semanticfield/1')

    def test_values(self):
        self.app.get_dt('/values?parameter=1-1')
        self.app.get_dt('/values?parameter=1-1&iSortingCols=1&iSortCol_0=1&sSearch_1=a')
        self.app.get_dt('/values?contribution=15&iSortingCols=1&iSortCol_0=1')
        self.app.get_dt('/values?contribution=15&sSearch_1=10')

    def test_contributors(self):
        self.app.get_dt('/contributor')

    def test_parameters(self):
        self.app.get_html('/meaning')
        self.app.get_dt('/meaning?semanticfield=1')
        self.app.get_dt('/meaning?sSearch_4=2&iSortingCols=1&iSortCol_0=4')
        self.app.get_html('/meaning/1-1')
        self.app.get_json('/meaning/1-1.geojson')

    def test_languages(self):
        self.app.get_html('/language')
        self.app.get_json('/language.geojson')
        self.app.get_html('/language/13')
        self.app.get_html('/language/13.snippet.html?parameter=1')

    def test_semanticfields(self):
        self.app.get_dt('/semanticfield')

    def test_contribution(self):
        self.app.get_html('/vocabulary')
        self.app.get_html('/vocabulary/1')
        self.app.get('/vocabulary/1.md.txt')

    def test_words(self):
        self.app.get_dt('/units?type_=donor&language=13')
        self.app.get_dt('/units?type_=recipient&language=13')
        self.app.get_dt('/units?type_=recipient&language=13&sSearch_1=earlier')
        self.app.get_html('/word/72141423147775096')
        self.app.get_html('/word/7651652268706718')
