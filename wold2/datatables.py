"""
custom datatables for wold2
"""
from sqlalchemy import Integer
from sqlalchemy.sql.expression import cast
from sqlalchemy.orm import joinedload, joinedload_all, aliased, contains_eager

from clld.util import dict_merged
from clld.web.datatables import Values, Languages, Contributors
from clld.web.datatables.base import Col, LinkCol, PercentCol, IntegerIdCol, LinkToMapCol
from clld.web.datatables.contribution import Contributions, CitationCol, ContributorsCol
from clld.web.datatables.unit import Units
from clld.web.datatables.parameter import Parameters
from clld.web.util.htmllib import HTML
from clld.web.util.helpers import text2html, link
from clld.db.meta import DBSession
from clld.db.models import common
from clld.db.util import get_distinct_values

from wold2.models import (
    Loan, Word, Counterpart, WoldLanguage, Vocabulary, Meaning, SemanticField,
)
from wold2.util import source_words, hb_borrowed_score, hb_age_score, hb_simplicity_score


class RelationCol(Col):
    __kw__ = {'choices': ['immediate', 'earlier']}

    def search(self, qs):
        return Loan.relation == qs

    def format(self, item):
        coll = item.source_word_assocs if self.dt.type == 'donor' \
               else item.target_word_assocs
        attr = 'source_word' if self.dt.type == 'donor' else 'target_word'
        return ', '.join(set([l.relation for l in coll if getattr(l, attr).language == self.dt.language]))
        return '%s' % list(['%s (%s) -> %s (%s)' % (l.source_word, l.source_word.language, l.target_word, l.target_word.language) for l in coll if getattr(l, attr).language == self.dt.language])


class RelWordsCol(Col):
    def format(self, item):
        coll = item.source_word_assocs if self.dt.type == 'donor' \
               else item.target_word_assocs
        attr = 'source_word' if self.dt.type == 'donor' else 'target_word'
        return ', '.join([link(self.dt.req, getattr(l, attr)) for l in coll if getattr(l, attr).language == self.dt.language])


class Words(Units):
    def __init__(self, req, model, type_=None, **kw):
        self.type = type_
        if 'type_' in req.params:
            self.type = req.params['type_']
        assert self.type in ['donor', 'recipient']
        self.Donor = aliased(WoldLanguage)
        self.Recipient = aliased(WoldLanguage)
        self.SourceWord = aliased(Word)
        self.TargetWord = aliased(Word)
        Units.__init__(self, req, model, eid='datatable-%s' % self.type, **kw)

    def base_query(self, query):
        if self.type == 'donor':
            # we are looking for target words borrowed from english into other languages:
            query = DBSession.query(common.Unit)\
                .join(self.Recipient, self.Recipient.pk == common.Unit.language_pk)\
                .join(Loan, common.Unit.pk == Loan.target_word_pk)\
                .join(self.SourceWord, Loan.source_word_pk == self.SourceWord.pk)\
                .join(self.Donor, self.Donor.pk == self.SourceWord.language_pk)\
                .filter(self.Donor.pk == self.language.pk)\
                .options(contains_eager(Word.source_word_assocs))
        else:
            query = DBSession.query(common.Unit)\
                .join(self.Donor, self.Donor.pk == common.Unit.language_pk)\
                .join(Loan, common.Unit.pk == Loan.source_word_pk)\
                .join(self.TargetWord, Loan.target_word_pk == self.TargetWord.pk)\
                .join(self.Recipient, self.Recipient.pk == self.TargetWord.language_pk)\
                .filter(self.Recipient.pk == self.language.pk)\
                .options(contains_eager(Word.target_word_assocs))
        return query

    def col_defs(self):
        lang = self.Recipient if self.type == 'donor' else self.Donor
        ltitle = 'Recipient language' if self.type == 'donor' else 'Donor languoid'
        res = [
            RelWordsCol(
                self,
                'self',
                sTitle='Borrowed words' if self.type !='donor' else 'Source words',
                model_col=self.SourceWord.name if self.type == 'donor' else self.TargetWord.name),
            RelationCol(self, 'relation'),
            LinkCol(self, 'language', sTitle=ltitle, get_obj=lambda i: i.language, model_col=lang.name),
            LinkCol(self, 'other', model_col=common.Unit.name, sTitle='Borrowed word' if self.type =='donor' else 'Source word'),
            LinkToMapCol(self, 'm', get_obj=lambda i: i.language, map_id=self.type + '-map'),
        ]
        return res

    def xhr_query(self):
        return dict_merged(super(Units, self).xhr_query(), type_=self.type)

    def get_options(self):
        return {'iDisplayLength': 20}


class LWTCodeCol(Col):
    """special handling for lwt code
    """
    __kw__ = {
        'sTitle': 'LWT code',
        'sDescription': "The Loanword Typology code is the identifier of the Loanword "
        "Typology meaning. Sorting by LWT Code sorts the words thematically by semantic "
        "field.",
    }

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


class SourceWordsCol(Col):
    def format(self, item):
        return source_words(self.dt.req, item.word)


class CoreListCol(Col):
    __kw__ = dict(
        model_col=Meaning.core_list,
        sFilter='True',
        sDescription="This column indicates whether the word is a counterpart "
        "for one of the 1460 core LWT meanings.")


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
            return query.join(common.ValueSet.parameter)\
                .filter(common.ValueSet.contribution_pk == self.contribution.pk)\
                .options(
                    joinedload_all(Counterpart.word, Word.source_word_assocs),
                    joinedload_all(common.Value.valueset, common.ValueSet.parameter))

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
        word_form_col = LinkCol(
            self, 'word_form',
            model_col=Word.name,
            get_object=get_word,
            sDescription="<p>The word is given in the usual orthography or "
            "transcription, and in the usual citation form.</p><p>Click on a word to "
            "get more information than is shown in this table.</p>")
        borrowed_col = Col(
            self, 'borrowed',
            model_col=Word.borrowed,
            get_object=get_word,
            choices=get_distinct_values(Word.borrowed),
            sDescription="<p>There are five borrowed statuses, reflecting decreasing "
            "likelihood that the word is a loanword:</p><ol>"
            "<li>clearly borrowed</li><li>probably borrowed</li><li>perhaps borrowed</li>"
            "<li>very little evidence for borrowing</li>"
            "<li>no evidence for borrowing</li></ol>")

        if self.parameter:
            return [
                IntegerIdCol(
                    self, 'vocid',
                    sTitle='Voc. ID',
                    model_col=common.Contribution.id,
                    get_object=get_vocabulary,
                    sDescription="The vocabulary ID corresponds to the ordering to the "
                    "chapters on the book <em>Loanwords in the World's Languages</em>. "
                    "Languages are listed in rough geographical order from west to east, "
                    "from Africa via Europe to Asia and the Americas, so that "
                    "geographically adjacent languages are next to each other."),
                VocabularyCol(self, 'vocabulary', get_object=get_vocabulary),
                word_form_col,
                borrowed_col,
                CounterpartScoreCol(self, 'borrowed_score'),
                CounterpartScoreCol(self, 'age_score'),
                CounterpartScoreCol(self, 'simplicity_score'),
            ]
        if self.contribution:
            return [
                word_form_col,
                LWTCodeCol(
                    self, 'lwt_code',
                    get_object=get_meaning),
                LinkCol(
                    self, 'meaning',
                    model_col=common.Parameter.name,
                    get_object=get_meaning,
                    sDescription="This column shows the labels of the Loanword Typology "
                    "meanings. By clicking on a meaning label, you get more information "
                    "about the meaning, as well as a list of all words that are "
                    "counterparts of that meaning."),
                CoreListCol(self, 'core_list', get_object=get_meaning),
                borrowed_col,
                SourceWordsCol(
                    self, 'source_words',
                    bSearchable=False,
                    bSortable=False,
                    sDescription="For (possible) loanwords, this column shows the words "
                    "in the source languages that served as models."),
            ]

        return []

"""
    <div id="hb_period" class="help-ballon-content">
      This is the time period during which the word is hypothesized to have come into the
      language as a loanword, or during which it is first attested, or for which it can be reconstructed.
    </div>

    <div id="hb_original_script" class="help-ballon-content">
      This gives the usual written form for languages that do not use the Latin script.
    </div>

"""


class WoldLanguages(Languages):

    def base_query(self, query):
        query = Languages.base_query(self, query)
        return query.outerjoin(
            common.Contribution, WoldLanguage.vocabulary_pk == common.Contribution.pk)

    def col_defs(self):
        return [
            IntegerIdCol(self, 'id', sTitle='ID'),
            LinkCol(self, 'language_name', route_name='language'),
            Col(self, 'language_family', model_col=WoldLanguage.affiliation),
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
            IntegerIdCol(
                self, 'id',
                sTitle="ID",
                sDescription="The vocabulary ID number corresponds to the ordering to the "
                "chapters on the book <em>Loanwords in the World's Languages</em>. "
                "Languages are listed in rough geographical order from west to east, "
                "from Africa via Europe to Asia and the Americas, so that "
                "geographically adjacent languages are next to each other."),
            VocabularyCol(
                self, 'vocabulary',
                sDescription="<p>Each vocabulary of WOLD is a separate electronic "
                "publication with a separate author or team of authors. Each vocabulary "
                "has a characteristic colour in WOLD.</p><p>Click on a vocabulary to "
                "see the words (loanwords and nonloanwords) and their properties.</p>"),
            ContributorsCol(
                self, 'contributor',
                sDescription="The authors are experts of the language and its history. "
                "They also contributed a prose chapter on the borrowing situation in "
                "their language that was published in the book "
                "Loanwords in the World's Languages."),
            Col(self, 'n',
                sTitle='Number of words',
                model_col=Vocabulary.count_words,
                sDescription="There would be 1814 words in each vocabulary, "
                "corresponding to the 1814 Loanword Typology meanings, if each meaning "
                "had exactly one counterpart, and if all the counterparts were "
                "different words. But many (\"polysomous\") words are counterparts of "
                "several meanings, many meanings have several word counterparts "
                "(\"synonyms\", or \"subcounterparts\"), and many meanings have no "
                "counterparts at all, so the number of words in each database varies "
                "considerably."),
            PercentCol(
                self, 'p',
                sTitle='Percentage of loanwords',
                model_col=Vocabulary.borrowed_score,
                sDescription="This gives the percentage of words in each language that "
                "are \"clearly borrowed\" or \"probably borrowed\"."),
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
            CoreListCol(self, 'core_list'),
            Col(self, 'cat', sTitle='Semantic category',
                model_col=Meaning.semantic_category, choices=get_distinct_values(Meaning.semantic_category)),
            SemanticFieldCol(self, 'sf', sTitle='Semantic field'),
            MeaningScoreCol(
                self, 'borrowed_score', sDescription=unicode(hb_borrowed_score())),
            MeaningScoreCol(
                self, 'age_score', sDescription=unicode(hb_age_score())),
            MeaningScoreCol(
                self, 'simplicity_score', sDescription=unicode(hb_simplicity_score())),
            Col(self, 'representation',
                model_col=Meaning.representation,
                sDescription="This column shows how many counterparts for this meaning "
                "there are in the 41 languages. The number can be higher than 41 because "
                "a language may have several counterparts for one meaning (\"synonyms\"),"
                " and it may be lower than 41, because not all languages may have a "
                "counterpart for a meaning. "),
        ]


def includeme(config):
    config.register_datatable('units', Words)
    config.register_datatable('values', Counterparts)
    config.register_datatable('languages', WoldLanguages)
    config.register_datatable('contributors', Authors)
    config.register_datatable('contributions', Vocabularies)
    config.register_datatable('parameters', Meanings)
