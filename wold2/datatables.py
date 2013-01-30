"""
custom datatables for wold2
"""
from sqlalchemy import desc

from clld.web.datatables import Values, Languages, Contributors
from clld.web.datatables.base import Col, LinkCol
from clld.web.util.htmllib import HTML
from clld.web.util.helpers import text2html

from wold2.models import Word, Counterpart, Vocabulary, WoldLanguage


class WordCol(Col):
    def order(self):
        return Word.name

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
        if item.vocabulary:
            return HTML.div(
                item.vocabulary.name,
                style="background-color: #%s;" % item.vocabulary.color,
                class_='dt-full-cell')
        return ''


class IdCol(Col):
    def order(self):
        return WoldLanguage.pk


class WoldLanguages(Languages):

    def base_query(self, query):
        query = Languages.base_query(self, query)
        return query.outerjoin(Vocabulary, WoldLanguage.vocabulary_pk == Vocabulary.pk)

    def col_defs(self):
        return [
            IdCol(self, 'id'),
            LinkCol(self, 'name', route_name='language'),
            Col(self, 'family'),
            VocabularyCol(self, 'vocabulary'),
        ]


class WoldContributors(Contributors):
    """In WOLD, the contributors table does also list the address.
    """
    def col_defs(self):
        class AddressCol(Col):
            def format(self, item):
                return text2html(item.address)

        res = Contributors.col_defs(self)
        return [res[0]] + [AddressCol(self, 'address')] + res[1:]
