from __future__ import unicode_literals, division, absolute_import, print_function
import os

from sqlalchemy.orm import joinedload_all

from clldutils.path import Path
from clldutils.misc import lazyproperty
from clld.db.models.common import Identifier, Unit, UnitValue
from clld.interfaces import IParameter, ILanguage, IIndex, IContribution, ICldfDataset
from clld.web.adapters import GeoJsonLanguages, GeoJsonParameter
from clld.web.adapters.cldf import CldfDownload, url_template
from pycldf import Wordlist
try:
    from pyconcepticon.api import Concepticon
except ImportError:
    Concepticon = None

from wold2.models import Counterpart


_venvs = Path(os.path.expanduser('~')).joinpath('venvs')


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


props = """\
 age_label
 borrowed_base
 calqued
 colonial_word
 comment_on_borrowed
 comment_on_word_form
 effect
 etymological_note
 gloss
 grammatical_info
 integration
 lexical_stratum
 loan_history
 numeric_frequency
 original_script
 other_comments
 reference
 register
 relative_frequency
 salience
 word_source""".split()


class CldfDictionary(CldfDownload):
    #
    # FIXME: implement fully once CLDF support in clld is better!
    #
    @lazyproperty
    def concepticon(self):
        res = {}
        if Concepticon:
            concepticon = Concepticon(_venvs.joinpath('concepticon', 'concepticon-data'))
            for concept in concepticon.conceptlist('Haspelmath-2009-1460'):
                res[concept['WOLD_ID']] = concept['CONCEPTICON_ID']
        return res

    def columns(self, req):
        return [
            'ID',
            {
                'name': 'Language_ID',
                'valueUrl': Identifier(type='glottolog', name='{Language_ID}').url()},
            'Language_name',
            {
                'name': 'Parameter_ID',
                'valueUrl': 'http://concepticon.clld.org/parameters/{Parameter_ID}'},
            'Parameter_name',
            {
                'name': 'WOLD_Meaning_ID',
                'valueUrl': url_template(req, 'parameter', 'WOLD_Meaning_ID')},
            'Value',
            'Source',
            'Comment',
            {
                'name': 'Word_ID',
                'valueUrl': url_template(req, 'unit', 'Word_ID')},
            'Borrowed',
            'Borrowed_score',
            #{
            #    'name': 'Borrowed_score',
            #    'datatype': 'float'},
            'Analyzability',
            'Simplicity_score',
            #{
            #    'name': 'Simplicity_score',
            #    'datatype': 'float'},
            'age',
            'contact_situation',
        ] + props

    def row(self, req, value, refs):
        if not value.valueset.parameter.core_list:
            return
        return [
            value.id,
            value.valueset.language.glottocode,
            value.valueset.language.name,
            self.concepticon[value.valueset.parameter.id],
            value.valueset.parameter.name,
            value.valueset.parameter.id,
            value.word.name,
            refs,
            value.valueset.source or '',
            value.word.id,
            value.word.borrowed,
            value.word.borrowed_score,
            value.word.analyzability,
            value.word.simplicity_score,
            value.word.age,
            value.word.contact_situation
        ] + [value.word.jsondata.get(prop) or '' for prop in props]


def includeme(config):
    config.register_adapter(GeoJsonMeaning, IParameter)
    config.register_adapter(
        WoldGeoJsonLanguages,
        ILanguage,
        IIndex,
        WoldGeoJsonLanguages.mimetype)
