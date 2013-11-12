from __future__ import unicode_literals

from clld.web.adapters import GeoJsonLanguages, GeoJsonParameter


class GeoJsonMeaning(GeoJsonParameter):
    def feature_properties(self, ctx, req, valueset):
        return {
            'values': list(valueset.values),
            'label': ', '.join(v.word.name for v in valueset.values)}


class WoldGeoJsonLanguages(GeoJsonLanguages):
    def feature_properties(self, ctx, req, feature):
        res = GeoJsonLanguages.feature_properties(self, ctx, req, feature)
        res['recipient'] = 'y' if feature.vocabulary_pk else 'n'
        return res
