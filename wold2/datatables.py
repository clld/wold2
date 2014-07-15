"""
custom datatables for wold2
"""
from __future__ import unicode_literals, division, absolute_import, print_function

from sqlalchemy.orm import joinedload, joinedload_all, aliased, contains_eager

from clld.util import dict_merged
from clld.web.datatables import Values, Languages
from clld.web.datatables.base import (
    Col, LinkCol, PercentCol, IntegerIdCol, LinkToMapCol, DataTable,
)
from clld.web.datatables.contribution import Contributions, CitationCol, ContributorsCol
from clld.web.datatables import contributor
from clld.web.datatables.unit import Units
from clld.web.datatables.parameter import Parameters
from clld.web.util.htmllib import HTML
from clld.web.util.helpers import link
from clld.db.meta import DBSession
from clld.db.models import common
from clld.db.util import get_distinct_values

from wold2.models import (
    Loan, Word, Counterpart, WoldLanguage, Vocabulary, Meaning, SemanticField,
)
from wold2.util import source_words, hb_borrowed_score, hb_age_score, hb_simplicity_score


class RelationCol(Col):
    __kw__ = {
        'choices': ['immediate', 'earlier'],
        'sDescription': "Whether a word was contributed directly (immediate) or "
        " indirectly (earlier), i.e. via another, intermediate donor languoid, to "
        "the recipient language."}

    def search(self, qs):
        return Loan.relation == qs

    def format(self, item):
        coll = item.source_word_assocs if self.dt.type == 'donor' \
            else item.target_word_assocs
        attr = 'source_word' if self.dt.type == 'donor' else 'target_word'
        return ', '.join(set(
            [l.relation for l in coll if getattr(l, attr).language == self.dt.language]))


class RelWordsCol(Col):
    def format(self, item):
        coll = item.source_word_assocs if self.dt.type == 'donor' \
            else item.target_word_assocs
        attr = 'source_word' if self.dt.type == 'donor' else 'target_word'
        return ', '.join([link(self.dt.req, getattr(l, attr)) for l in coll
                          if getattr(l, attr).language == self.dt.language])


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
        ldesc = {
            'donor': "These are the names of languages and families from which the "
            "recipient language borrowed words directly or indirectly.",
            'recipient': "These are the names of recipient languages that borrowed words "
            "directly or indirectly from this languoid."}[self.type]
        w1desc = {
            'donor': "%s words contributed to other languages." % self.language.name,
            'recipient': "%s words borrowed from other languages." % self.language.name,
        }[self.type]
        w2desc = {
            'donor': "Words borrowed from %s." % self.language.name,
            'recipient': "Words contributed to %s." % self.language.name,
        }[self.type]
        res = [
            RelWordsCol(
                self,
                'self',
                sTitle='Borrowed words' if self.type != 'donor' else 'Source words',
                sDescription=w1desc,
                model_col=self.SourceWord.name
                if self.type == 'donor' else self.TargetWord.name),
            RelationCol(self, 'relation'),
            LinkCol(
                self, 'language',
                sTitle=ltitle, sDescription=ldesc,
                get_obj=lambda i: i.language, model_col=lang.name),
            LinkCol(
                self, 'other',
                model_col=common.Unit.name,
                sTitle='Borrowed word' if self.type == 'donor' else 'Source word',
                sDescription=w2desc),
            LinkToMapCol(
                self, 'm', get_obj=lambda i: i.language, map_id=self.type + '-map'),
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
        return ''  # pragma: no cover


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

        return query  # pragma: no cover

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
            self, 'borrowed', sTitle='Borrowed status',
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

        return []  # pragma: no cover


class WoldLanguages(Languages):

    def base_query(self, query):
        query = Languages.base_query(self, query)
        return query.outerjoin(
            common.Contribution, WoldLanguage.vocabulary_pk == common.Contribution.pk)

    def col_defs(self):
        return [
            IntegerIdCol(self, 'id', sTitle='ID'),
            LinkCol(
                self, 'language_name', route_name='language',
                sDescription="This is the name of the language (or family, in the case "
                "of donor languages) that was adopted in the World Loanword Database. "
                "Alternative names can be found on the individual language pages."),
            Col(self, 'language_family', model_col=WoldLanguage.affiliation,
                sDescription="This is the name of the highest family that is generally "
                "accepted to which the language belongs. "),
            VocabularyCol(
                self, 'vocabulary', get_object=lambda i: i.vocabulary,
                sDescription="For recipient languages, this column shows the "
                "corresponding vocabulary."),
        ]


class Authors(contributor.Contributors):
    """In WOLD, the contributors table does also list the address.
    """
    def col_defs(self):
        class ContributionsCol(contributor.ContributionsCol):
            def format(self, item):
                return HTML.ul(
                    *[HTML.li(
                        link(self.dt.req, c.contribution),
                        style="background-color: #%s;" % c.contribution.color,
                        class_='dt-full-cell') for c in item.contribution_assocs],
                    class_='nav nav-pills nav-stacked')

        return [
            contributor.NameCol(self, 'name'),
            ContributionsCol(self, 'Contributions'),
            contributor.AddressCol(self, 'address'),
        ]


class Vocabularies(Contributions):
    def col_defs(self):
        return [
            # ID, Vocabulary, Authors, Number of words, Percentage of loanwords, cite
            IntegerIdCol(
                self, 'id',
                sTitle="ID",
                sDescription="The vocabulary ID number corresponds to the ordering to the"
                " chapters on the book <em>Loanwords in the World's Languages</em>. "
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
        kw['choices'] = [(sf.pk, sf.name) for sf in
                         DBSession.query(SemanticField).order_by(SemanticField.pk)]
        super(SemanticFieldCol, self).__init__(*args, **kw)

    def format(self, item):
        return item.semantic_field.name

    def order(self):
        return Meaning.semantic_field_pk

    def search(self, qs):
        return Meaning.semantic_field_pk == int(qs)


class Meanings(Parameters):
    __constraints__ = [SemanticField]

    def base_query(self, query):
        query = query.join(SemanticField)
        if self.semanticfield:
            query = query.filter(SemanticField.pk == self.semanticfield.pk)
        return query

    def col_defs(self):
        return filter(lambda col: not self.semanticfield or col.name != 'sf', [
            LWTCodeCol(self, 'lwt_code'),
            LinkCol(
                self, 'name', sTitle='Meaning',
                sDescription="This column shows the labels of the Loanword Typology "
                "meanings. By clicking on a meaning label, you get more information "
                "about the meaning, as well as a list of all words that are counterparts "
                "of that meaning."),
            CoreListCol(self, 'core_list'),
            Col(self, 'cat', sTitle='Semantic category',
                sDescription="Meanings were assigned to semantic categories with "
                "word-class-like labels: nouns, verbs, adjectives, adverbs, function "
                "words. No claim is made about the grammatical behavior of words "
                "corresponding to these meanings. The categories are intended to be "
                "purely semantic.",
                model_col=Meaning.semantic_category,
                choices=get_distinct_values(Meaning.semantic_category)),
            SemanticFieldCol(
                self, 'sf', sTitle='Semantic field',
                sDescription="The first 22 fields are the fields of the Intercontinental "
                "Dictionary Series meaning list, proposed by Mary Ritchie Key, and "
                "ultimately based on Carl Darling Buck's (1949) Dictionary of selected "
                "synonyms in the principal Indo-European languages. The other two fields "
                "were added for the Loanword Typology project."),
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
        ])


class SemanticFieldScoreCol(ScoreCol):
    __model__ = SemanticField


class NumberOfMeanings(Col):
    __kw__ = {'sClass': 'right'}

    def format(self, item):
        return len(item.meanings)


class SemanticFields(DataTable):
    def col_defs(self):
        return [
            IntegerIdCol(
                self, 'id',
                sDescription="The number in this column is the semantic field number. It "
                "is the first part of the Loanword Typology Code of the words in the "
                "corresponding field."),
            LinkCol(
                self, 'name',
                sDescription="The first 22 fields are the fields of the Intercontinental "
                "Dictionary Series meaning list, proposed by Mary Ritchie Key, and "
                "ultimately based on Carl Darling Buck's (1949) <i>Dictionary of selected"
                " synonyms in the principal Indo-European languages</i>. The other two "
                "fields were added for the Loanword Typology project."),
            NumberOfMeanings(
                self, 'number_of_meanings',
                sDescription="This gives the number of different meanings in each "
                "semantic field."),
            SemanticFieldScoreCol(
                self, 'borrowed_score', sDescription=unicode(hb_borrowed_score())),
            SemanticFieldScoreCol(
                self, 'age_score', sDescription=unicode(hb_age_score())),
            SemanticFieldScoreCol(
                self, 'simplicity_score', sDescription=unicode(hb_simplicity_score())),
        ]


def includeme(config):
    config.register_datatable('units', Words)
    config.register_datatable('values', Counterparts)
    config.register_datatable('languages', WoldLanguages)
    config.register_datatable('contributors', Authors)
    config.register_datatable('contributions', Vocabularies)
    config.register_datatable('parameters', Meanings)
    config.register_datatable('semanticfields', SemanticFields)
