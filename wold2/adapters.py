from sqlalchemy.orm import joinedload

from clld.db.meta import DBSession
from clld.db.models.common import Parameter, Language, Value, Contribution
from clld.interfaces import IParameter, ILanguage, IIndex
from clld.web.adapters import GeoJsonLanguages, GeoJsonParameter
try:
    from pyconcepticon.api import Concepticon
except ImportError:
    Concepticon = None

from wold2.models import Counterpart, Meaning, Loan, Word


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


def includeme(config):
    config.register_adapter(GeoJsonMeaning, IParameter)
    config.register_adapter(
        WoldGeoJsonLanguages,
        ILanguage,
        IIndex,
        WoldGeoJsonLanguages.mimetype)
