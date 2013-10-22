from sqlalchemy.orm import aliased

from clld.web.util.helpers import link
from clld.db.meta import DBSession

from wold2.models import WoldLanguage, Word, Loan


def get_meaning_properties(req, ctx):
    for attr, converter in [
        ('description', lambda s: s),
        ('typical_context', lambda s: s),
        ('semantic_field', lambda sf: link(req, sf)),
        ('semantic_category', lambda s: s),
        ('borrowed_score', lambda f: '{0:.2f}'.format(f)),
        ('age_score', lambda f: '{0:.2f}'.format(f)),
        ('simplicity_score', lambda f: '{0:.2f}'.format(f)),
    ]:
        yield (attr.capitalize().replace('_', ' '), converter(getattr(ctx, attr)))


def get_related_languages(ctx, req):
    Donor = aliased(WoldLanguage)
    Recipient = aliased(WoldLanguage)
    SourceWord = aliased(Word)
    TargetWord = aliased(Word)

    if req.params.get('t') == 'recipient':
        q = DBSession.query(Donor)\
            .join(SourceWord, Donor.pk == SourceWord.language_pk)\
            .join(Loan, Loan.source_word_pk == SourceWord.pk)\
            .join(TargetWord, Loan.target_word_pk == TargetWord.pk)\
            .join(Recipient, Recipient.pk == TargetWord.language_pk)\
            .filter(Recipient.pk == ctx.pk)
    else:
        # return ctx as donor, other languages as recipients
        q = DBSession.query(Recipient)\
            .join(TargetWord, Recipient.pk == TargetWord.language_pk)\
            .join(Loan, Loan.target_word_pk == TargetWord.pk)\
            .join(SourceWord, Loan.source_word_pk == SourceWord.pk)\
            .join(Donor, Donor.pk == SourceWord.language_pk)\
            .filter(Donor.pk == ctx.pk)
    return q


def get_related_languages_geojson(ctx, req, langs):
    def make_feature(lang, recipient):
        return {
            'type': 'Feature',
            'geometry': {
                'type': 'Point',
                'coordinates': [lang.longitude, lang.latitude]},
            'properties': {
                'name': lang.name,
                'id': lang.id,
                'recipient': 'y' if recipient else 'n',
            }
        }

    features = [make_feature(ctx, req.params.get('t') != 'donor')]

    for lang in langs:
        features.append(make_feature(lang, req.params.get('t') == 'donor'))

    return {'type': 'FeatureCollection', 'properties': {}, 'features': features}
