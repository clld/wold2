from sqlalchemy.orm import joinedload

from clld.db.meta import DBSession
from clld.db.models.common import Parameter, Language, Value, Contribution
from clld.interfaces import IParameter, ILanguage, IIndex, ICldfConfig
from clld.web.adapters import GeoJsonLanguages, GeoJsonParameter
from clld.web.adapters.cldf import CldfConfig, url_template
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


class WoldCldfConfig(CldfConfig):
    def custom_schema(self, req, ds):
        ds.add_columns(
            'FormTable',
            {'name': 'Word_ID', 'valueUrl': 'http://wold.clld.org/word/{Word_ID}'},
            {'name': 'BorrowedScore', 'datatype': 'float'},
            {'name': 'AgeScore', 'datatype': 'float'},
            {'name': 'SimplicityScore', 'datatype': 'float'},
            'Borrowed',
            'Analyzability',
            'Age',
            'ContactSituation',
            *props)
        ds.add_columns(
            'ParameterTable',
            'SemanticField',
            {'name': 'BorrowedScore', 'datatype': 'float'},
            {'name': 'AgeScore', 'datatype': 'float'},
            {'name': 'SimplicityScore', 'datatype': 'float'},
            'SemanticCategory',
            'IDS_code',
            'TypicalContext',
            {'name': 'CoreList', 'datatype': 'boolean'},
        )
        ds['ParameterTable', 'ID'].valueUrl = url_template(req, 'parameter', 'ID')
        ds.add_component(
            'BorrowingTable',
            'relation',
            {'name': 'certain', 'datatype': 'boolean'},
            'http://cldf.clld.org/v1.0/terms.rdf#languageReference',
        )
        ds['LanguageTable', 'ID'].valueUrl = url_template(req, 'language', 'ID')
        for v in DBSession.query(Contribution):
            ds.add_sources("@misc{%s,\nnote={%s}}" % (v.id, v.jsondata['fd_reference']))

    def custom_tabledata(self, req, tabledata):
        loans, count = [], 0
        languages = {l.pk: l.id for l in DBSession.query(Language)}
        for loan in DBSession.query(Loan).options(
            joinedload(Loan.source_word),
            joinedload(Loan.target_word).joinedload(Word.counterparts)
        ):
            for cp in loan.target_word.counterparts:
                count += 1
                loans.append({
                    'ID': str(count),
                    'Target_Form_ID': cp.id,
                    'Comment': loan.source_word.name,
                    'Language_ID': languages[loan.source_word.language_pk],
                    'relation': loan.relation,
                    'certain': loan.certain})
        tabledata['BorrowingTable'] = loans
        return tabledata

    def query(self, model):
        q = CldfConfig.query(self, model)
        if model == Parameter:
            q = q.options(joinedload(Meaning.semantic_field))
        if model == Value:
            q = q.options(joinedload(Counterpart.word).joinedload(Word.unitvalues))
        return q

    def convert(self, model, item, req):
        res = CldfConfig.convert(self, model, item, req)
        if model == Parameter:
            res.update(
                SemanticField=item.semantic_field.name,
                SemanticCategory=item.semantic_category,
                IDS_code=item.ids_code,
                TypicalContext=item.typical_context,
                CoreList=item.core_list,
                BorrowedScore=item.borrowed_score,
                AgeScore=item.age_score,
                SimplicityScore=item.simplicity_score,
            )
        if model == Value:
            res['Word_ID'] = item.word.id
            res.update({p: item.word.jsondata.get(p) or '' for p in props})
            res.update(
                Source=[item.valueset.contribution.id],
                BorrowedScore=item.word.borrowed_score,
                AgeScore=item.word.age_score,
                SimplicityScore=item.word.simplicity_score,
                Borrowed=item.word.borrowed,
                Analyzability=item.word.analyzability,
                Age=item.word.age.unitdomainelement.name if item.word.age else None,
                ContactSituation=item.word.contact_situation.unitdomainelement.name if item.word.contact_situation else None,
            )
        return res


def includeme(config):
    config.registry.registerUtility(WoldCldfConfig(), ICldfConfig)
    config.register_adapter(GeoJsonMeaning, IParameter)
    config.register_adapter(
        WoldGeoJsonLanguages,
        ILanguage,
        IIndex,
        WoldGeoJsonLanguages.mimetype)
