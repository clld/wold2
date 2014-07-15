from __future__ import unicode_literals, division, absolute_import, print_function

from clld.web.maps import Map, Layer, Legend, ParameterMap
from clld.web.adapters.geojson import GeoJson
from clld.web.util.htmllib import HTML, literal


ICONS = {'recipient': 'dff0000', 'donor': 'c4d6cee'}


def icon_url(req, type_):
    return req.static_url('clld:web/static/icons/%s.png' % ICONS[type_])


def legend_items(req):
    for type, label in [('recipient', 'recipient language'), ('donor', 'donor languoid')]:
        yield HTML.label(
            HTML.img(src=icon_url(req, type), height='20', width='20'),
            literal(' ' + label),
            style='margin-left: 1em; margin-right: 1em;')


class LanguagesMap(Map):
    def get_options(self):
        return {'style_map': 'wold_languages'}

    def get_legends(self):
        yield Legend(self, 'values', list(legend_items(self.req)), label='Legend')


class LanguageGeoJson(GeoJson):
    def feature_iterator(self, ctx, req):
        return [self.obj[0]] + list(self.obj[1])


class RecipientGeoJson(LanguageGeoJson):
    def feature_properties(self, ctx, req, feature):
        return {'icon': icon_url(req, 'recipient' if feature == ctx else 'donor')}


class DonorGeoJson(LanguageGeoJson):
    def feature_properties(self, ctx, req, feature):
        return {'icon': icon_url(req, 'recipient' if feature != ctx else 'donor')}


class LanguageMap(Map):
    def get_layers(self):
        yield Layer(
            self.ctx.id,
            self.ctx.name,
            self.geojson((self.ctx, self.rel)).render(self.ctx, self.req, dump=False))

    def get_legends(self):
        yield Legend(self, 'values', list(legend_items(self.req)), label='Legend')

    def get_options(self):
        return {'show_labels': True}


class RecipientMap(LanguageMap):
    def __init__(self, ctx, req, rel):
        self.rel = rel
        self.geojson = RecipientGeoJson
        super(RecipientMap, self).__init__(ctx, req, eid='recipient-map')


class DonorMap(LanguageMap):
    def __init__(self, ctx, req, rel):
        self.rel = rel
        self.geojson = DonorGeoJson
        super(DonorMap, self).__init__(ctx, req, eid='donor-map')


class MeaningMap(ParameterMap):
    def get_options(self):
        return {'show_labels': True}


def includeme(config):
    config.register_map('languages', LanguagesMap)
    config.register_map('language', LanguageMap)
    config.register_map('parameter', MeaningMap)
