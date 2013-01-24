from sqlalchemy import desc

from clld.web.datatables import Values
from clld.web.datatables.base import Col

from wold2.models import Word, Counterpart


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
        return query.join(Word, Counterpart.word_pk==Word.pk)

    def col_defs(self):
        cols = Values.col_defs(self)
        return cols+[WordCol(self, 'word')]

        # vocabulary
        # word form
        # original script
        # borrowed status
        # borrowed score
        # age score
        # simplicity score
        # source words
