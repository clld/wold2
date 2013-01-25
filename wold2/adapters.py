from sqlalchemy.orm import aliased

from clld.db.meta import DBSession
from clld.web.adapters import GeoJsonLanguages, GeoJson

from wold2.models import WoldLanguage, Word


class WoldGeoJsonLanguages(GeoJsonLanguages):
    def feature_properties(self, ctx, req, feature):
        res = GeoJsonLanguages.feature_properties(self, ctx, req, feature)
        res['recipient'] = 'y' if feature.vocabulary_pk else 'n'
        return res


# custom geojson adapter for language detail page:
# language plus all languages with loanword relations

class WoldGeoJsonLanguage(GeoJson):
    def featurecollection_properties(self, ctx, req):
        return {}

    def feature_iterator(self, ctx, req):
        Donor = aliased(WoldLanguage)
        Recipient = aliased(WoldLanguage)
        SourceWord = aliased(Word)
        TargetWord = aliased(Word)

        if req.params.get('t') == 'donor':
            # return ctx as donor, other languages as recipients
            q = DBSession.query(Recipient)\
                .join(TargetWord, Recipient.pk == TargetWord.language_pk)\
                .join(Loan, Loan.target_word_pk == TargetWord.pk)\
                .join(SourceWord, Loan.source_word_pk == SourceWord.pk)\
                .join(Donor, Donor.pk == SourceWord.language_pk)\
                .filter(Donor.pk == ctx.pk)
            print('%s is donor for' % ctx.name)
            for l in q:
                print(l.name)
        else:
            # return ctx as recipient, other languages as donors
            pass
        return

    def feature_properties(self, ctx, req, feature):
        return {}

    def feature_coordinates(self, ctx, req, feature):
        """
        :return: lonlat
        """
        return [0.0, 0.0]
