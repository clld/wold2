from sqlalchemy import desc

from clld.web.datatables import Values, Languages
from clld.web.datatables.base import Col
from clld.web.util.htmllib import tag

from wold2.models import Word, Counterpart, Vocabulary, WoldLanguage


class WordCol(Col):
    def order(self, direction):
        return desc(Word.name) if direction == 'desc' else Word.name

    def search(self, qs):
        return Word.name.contains(qs)

    def format(self, item):
        return item.word.name


class Counterparts(Values):

    def base_query(self, query):
        query = Values.base_query(self, query)
        return query.join(Word, Counterpart.word_pk == Word.pk)

    def col_defs(self):
        cols = Values.col_defs(self)
        return cols + [WordCol(self, 'word')]

        # vocabulary
        # word form
        # original script
        # borrowed status
        # borrowed score
        # age score
        # simplicity score
        # source words


class VocabularyCol(Col):
    def search(self, qs):
        return Vocabulary.name.contains(qs)

    def format(self, item):
        #
        # TODO: color!!
        #
        if item.vocabulary:
            return tag('div', item.vocabulary.name,
                       **{'style': "background-color: #%s;" % item.vocabulary.color,
                          'class': 'dt-full-cell'})
        return ''


class IdCol(Col):
    def order(self, direction):
        return desc(WoldLanguage.pk) if direction == 'desc' else WoldLanguage.pk


class WoldLanguages(Languages):

    def base_query(self, query):
        query = Languages.base_query(self, query)
        return query.outerjoin(Vocabulary, WoldLanguage.vocabulary_pk == Vocabulary.pk)

    def col_defs(self):
        return [
            IdCol(self, 'id'),
            Col(self, 'name'),
            Col(self, 'family'),
            VocabularyCol(self, 'vocabulary'),
        ]
