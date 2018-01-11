import pytest

pytest_plugins = ['clld']


@pytest.mark.parametrize(
    "method,path",
    [
        ('get_html', '/'),
        ('get_html', '/terms'),
        ('get_html', '/semanticfield'),
        ('get_html', '/semanticfield/1'),
        ('get_dt', '/values?parameter=1-1'),
        ('get_dt', '/values?parameter=1-1&iSortingCols=1&iSortCol_0=1&sSearch_1=a'),
        ('get_dt', '/values?contribution=15&iSortingCols=1&iSortCol_0=1'),
        ('get_dt', '/values?contribution=15&sSearch_1=10'),
        ('get_dt', '/contributor'),
        ('get_html', '/meaning'),
        ('get_dt', '/meaning?semanticfield=1'),
        ('get_dt', '/meaning?sSearch_4=2&iSortingCols=1&iSortCol_0=4'),
        ('get_html', '/meaning/1-1'),
        ('get_json', '/meaning/1-1.geojson'),
        ('get_html', '/language'),
        ('get_json', '/language.geojson'),
        ('get_html', '/language/13'),
        ('get_html', '/language/13.snippet.html?parameter=1'),
        ('get_dt', '/semanticfield'),
        ('get_html', '/vocabulary'),
        ('get_html', '/vocabulary/1'),
        ('get', '/vocabulary/1.md.txt'),
        ('get_dt', '/units?type_=donor&language=13'),
        ('get_dt', '/units?type_=recipient&language=13'),
        ('get_dt', '/units?type_=recipient&language=13&sSearch_1=earlier'),
        ('get_html', '/word/72141423147775096'),
        ('get_html', '/word/7651652268706718'),
    ])
def test_pages(app, method, path):
    getattr(app, method)(path)
