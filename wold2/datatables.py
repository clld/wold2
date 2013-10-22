"""
custom datatables for wold2
"""
from sqlalchemy import Integer
from sqlalchemy.sql.expression import cast
from sqlalchemy.orm import joinedload, joinedload_all

from clld.web.datatables import Values, Languages, Contributors
from clld.web.datatables.base import Col, LinkCol, PercentCol, IntegerIdCol
from clld.web.datatables.contribution import Contributions, CitationCol, ContributorsCol
from clld.web.datatables.parameter import Parameters
from clld.web.util.htmllib import HTML
from clld.web.util.helpers import text2html, link
from clld.db.meta import DBSession
from clld.db.models import common
from clld.db.util import get_distinct_values

from wold2.models import Word, Counterpart, WoldLanguage, Vocabulary, Meaning, SemanticField


class LWTCodeCol(Col):
    """special handling for lwt code
    """
    __kw__ = {'sTitle': 'LWT code'}

    def format(self, item):
        return self.get_obj(item).id.replace('-', '.')

    def order(self):
        return Meaning.semantic_field_pk, Meaning.sub_code

    def search(self, qs):
        return Meaning.id.contains(qs.replace('.', '-'))


class ScoreCol(Col):
    """
    """
    __kw__ = {'sClass': 'right', 'input_size': 'mini'}

    def __init__(self, dt, name, **kw):
        assert name.endswith('_score')
        kw['sTitle'] = name.capitalize().replace('_', ' ')
        if hasattr(self, '__model__'):
            kw['model_col'] = getattr(self.__model__, name)
        super(ScoreCol, self).__init__(dt, name, **kw)

    def format(self, item):
        value = getattr(self.get_obj(item), self.model_col.name, None)
        if isinstance(value, float):
            return '%.2f' % value
        return ''


class CounterpartScoreCol(ScoreCol):
    __model__ = Word

    def get_obj(self, item):
        return item.word


class VocabularyCol(LinkCol):
    """special handling for links to vocabularies: we color-code the background.
    """
    def search(self, qs):
        return common.Contribution.name.contains(qs)

    def order(self):
        return common.Contribution.name

    def format(self, item):
        obj = self.get_obj(item)
        if obj:
            return HTML.div(
                link(self.dt.req, obj),
                style="background-color: #%s;" % obj.color,
                class_='dt-full-cell')
        return ''


class Counterparts(Values):
    """Lists of counterparts
    """
    def base_query(self, query):
        query = query.join(common.ValueSet).join(Word)\
            .options(
                joinedload(common.Value.valueset),
                joinedload(Counterpart.word))

        if self.parameter:
            # list counterparts for a meaning
            query = query.join(common.ValueSet.contribution)
            return query.filter(common.ValueSet.parameter_pk == self.parameter.pk)

        if self.contribution:
            # list "words" of a vocabulary
            query = query.join(common.ValueSet.parameter)
            return query.filter(common.ValueSet.contribution_pk == self.contribution.pk)

        return query

    def get_options(self):
        opts = super(Values, self).get_options()
        if self.contribution:
            opts['aaSorting'] = [[1, 'asc']]
        return opts

    def col_defs(self):
        get_word = lambda item: item.word
        get_vocabulary = lambda item: item.valueset.contribution
        get_meaning = lambda item: item.valueset.parameter

        res = []
        if self.parameter:
            res.append(IntegerIdCol(
                self, 'vocid',
                sTitle='Voc. ID',
                model_col=common.Contribution.id,
                get_object=get_vocabulary))
            res.append(VocabularyCol(self, 'vocabulary', get_object=get_vocabulary))

        res.append(LinkCol(
            self, 'word_form', model_col=Word.name, get_object=get_word))

        if self.contribution:
            res.append(LWTCodeCol(self, 'lwt_code', get_object=get_meaning))
            res.append(LinkCol(
                self, 'meaning', model_col=common.Parameter.name, get_object=get_meaning))

        res.extend([
            # original script
            Col(self, 'borrowed',
                model_col=Word.borrowed,
                get_object=get_word,
                choices=get_distinct_values(Word.borrowed)),
            CounterpartScoreCol(self, 'borrowed_score'),
            CounterpartScoreCol(self, 'age_score'),
            CounterpartScoreCol(self, 'simplicity_score'),
            # source words
        ])
        return res


class IdCol(Col):
    def order(self):
        return WoldLanguage.pk


class WoldLanguages(Languages):

    def base_query(self, query):
        query = Languages.base_query(self, query)
        return query.outerjoin(
            common.Contribution, WoldLanguage.vocabulary_pk == common.Contribution.pk)

    def col_defs(self):
        return [
            IdCol(self, 'id'),
            LinkCol(self, 'name', route_name='language'),
            Col(self, 'family'),
            VocabularyCol(self, 'vocabulary', get_object=lambda i: i.vocabulary),
        ]


class Authors(Contributors):
    """In WOLD, the contributors table does also list the address.
    """
    def col_defs(self):
        class AddressCol(Col):
            def format(self, item):
                return text2html(item.address)

        res = Contributors.col_defs(self)
        return [res[0]] + [AddressCol(self, 'address')] + res[1:]


class Vocabularies(Contributions):
    def col_defs(self):
        return [
            # ID, Vocabulary, Authors, Number of words, Percentage of loanwords, cite
            IntegerIdCol(self, 'id'),
            VocabularyCol(self, 'vocabulary'),
            ContributorsCol(self, 'contributor'),
            Col(self, '#', sDescription='Number of words', sClass='right', model_col=Vocabulary.count_words),
            PercentCol(self, '%', sDescription='Percentage of loanwords', model_col=Vocabulary.borrowed_score),
            CitationCol(self, 'cite'),
        ]


class MeaningScoreCol(ScoreCol):
    __model__ = Meaning


class SemanticFieldCol(Col):
    def __init__(self, *args, **kw):
        kw['choices'] = [(sf.pk, sf.name) for sf in DBSession.query(SemanticField).order_by(SemanticField.pk)]
        super(SemanticFieldCol, self).__init__(*args, **kw)

    def format(self, item):
        return item.semantic_field.name

    def order(self):
        return Meaning.semantic_field_pk

    def search(self, qs):
        return Meaning.semantic_field_pk == int(qs)


class Meanings(Parameters):
    def base_query(self, query):
        return query.join(SemanticField)

    def col_defs(self):
        return [
            # LWT code, Meaning, Semantic category, Semantic field, borrowed/age/simplicity score, Representation,
            LWTCodeCol(self, 'lwt_code'),
            LinkCol(self, 'name', sTitle='Meaning'),
            Col(self, 'cat', sTitle='Semantic category',
                model_col=Meaning.semantic_category, choices=get_distinct_values(Meaning.semantic_category)),
            SemanticFieldCol(self, 'sf', sTitle='Semantic field'),
            MeaningScoreCol(self, 'borrowed_score'),
            MeaningScoreCol(self, 'age_score'),
            MeaningScoreCol(self, 'simplicity_score'),
        ]
