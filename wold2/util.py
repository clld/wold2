from __future__ import unicode_literals
from cgi import escape

from sqlalchemy.orm import aliased

from clld.web.util.helpers import link, button, icon, text2html
from clld.web.util.htmllib import HTML, literal
from clld.db.meta import DBSession

from wold2.models import WoldLanguage, Word, Loan


def infobutton(desc, content_type='text', placement='right'):
    if not desc:
        return ''
    if content_type == 'text':
        desc = text2html(escape(desc, quote=True), mode='p')
    return button(
        icon('info-sign', inverted=True),
        **{
            'data-toggle': 'popover',
            'data-placement': placement,
            'data-content': desc,
            'class': ['btn-info', 'btn-mini', 'fieldinfo']})


def hb_score(name, description, domain):
    return HTML.div(
        HTML.p("""This gives the average {name} of all words corresponding to
this meaning. The following {name}s are assigned to
words depending on {description}:""".format(**locals())),
        HTML.table(
            HTML.thead(HTML.tr(
                HTML.th(' '), HTML.th('score'))),
            HTML.tbody(
                *[HTML.tr(HTML.td(label), HTML.td(score)) for label, score in domain])))


def hb_borrowed_score():
    domain = [
        ('1. clearly borrowed', '1.00'),
        ('2. probably borrowed', '0.75'),
        ('3. perhaps borrowed', '0.50'),
        ('4. very little evidence for borrowing', '0.25'),
        ('5. no evidence for borrowing', '0.00'),
    ]
    return hb_score('borrowed score', 'the degree of likelihood of borrowing', domain)


def hb_age_score():
    domain = [
        ('1. first attested or reconstructed earlier than 1000', '1.00'),
        ('2. earlier than 1500', '0.90'),
        ('3. earlier than 1800', '0.80'),
        ('4. earlier than 1900', '0.70'),
        ('5. earlier than 1950', '0.60'),
        ('6. earlier than 2007', '0.50'),
    ]
    return hb_score('age score', 'the estimated age of their age class', domain)


def hb_simplicity_score():
    domain = [
        ('1. unanalyzable', '1.00'),
        ('2. semi-analyzable', '0.75'),
        ('3. analyzable', '0.50'),
    ]
    return hb_score('simplicity score', 'their analyzability', domain)


def get_meaning_properties(req, ctx):
    for attr, info, converter in [
        ('description', None, lambda s: s),
        ('typical_context', None, lambda s: s),
        ('semantic_field', None, lambda sf: link(req, sf)),
        ('semantic_category', None, lambda s: s),
        ('borrowed_score', hb_borrowed_score(), lambda f: '{0:.2f}'.format(f)),
        ('age_score', hb_age_score(), lambda f: '{0:.2f}'.format(f)),
        ('simplicity_score', hb_simplicity_score(), lambda f: '{0:.2f}'.format(f)),
    ]:
        label = attr.capitalize().replace('_', ' ')
        if info:
            label = HTML.span(
                label, literal('&nbsp;'), infobutton(info, content_type='html'))
        yield (label, converter(getattr(ctx, attr)))


def property_name(property):
    return {
        'name': 'form',
        'description': 'free_meaning',
    }.get(property, property)


def property_label(property):
    return {
        'name': 'Word form',
        'meanings': 'LWT meaning(s)',
        'description': 'Word meaning',
        'comment_on_word_form': 'Comments on word',
        'comment_on_borrowed': 'Comments',
        'borrowed': 'Borrowed status',
        'calqued': 'Calqued status',
        'reference': 'Reference(s)',
        'early_romani_reconstruction': u"Early Romani reconstruction",
        'boretzky_and_igla_etymology': u"Boretzky & Igla's etymology",
        'manuss_et_al_etymology': u"M\u0101nu\u0161s et al. etymology",
        'vekerdi_etymology': u"Vekerdi's etymology",
        'turner_etymology': u"Turner's etymology",
        'other_etymologies': u"Other etymologies",
        'mayrhofer_etymology': u"Mayrhofer's etymology",
        'comparison_with_mandarin': u"Comparison with Mandarin",
        'comparison_with_korean': u"Comparison with Korean",
    }.get(property, property.replace('_', ' ').capitalize())


def get_related_languages(ctx, req):
    Donor = aliased(WoldLanguage)
    Recipient = aliased(WoldLanguage)
    SourceWord = aliased(Word)
    TargetWord = aliased(Word)

    qr = DBSession.query(Donor)\
        .join(SourceWord, Donor.pk == SourceWord.language_pk)\
        .join(Loan, Loan.source_word_pk == SourceWord.pk)\
        .join(TargetWord, Loan.target_word_pk == TargetWord.pk)\
        .join(Recipient, Recipient.pk == TargetWord.language_pk)\
        .filter(Recipient.pk == ctx.pk)
    qd = DBSession.query(Recipient)\
        .join(TargetWord, Recipient.pk == TargetWord.language_pk)\
        .join(Loan, Loan.target_word_pk == TargetWord.pk)\
        .join(SourceWord, Loan.source_word_pk == SourceWord.pk)\
        .join(Donor, Donor.pk == SourceWord.language_pk)\
        .filter(Donor.pk == ctx.pk)
    return qr, qd


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


def source_words(req, ctx):
    def _format(loan):
        if loan.source_word.name == 'Unidentifiable' and not loan.source_word.language and not loan.source_word.description:
            yield 'unidentifiable'
        else:
            yield link(req, loan.source_word)
            if loan.source_word.description and loan.source_word.description != '?':
                yield " '%s'" % loan.source_word.description
            if loan.source_word.language:
                yield ' '
                yield link(req, loan.source_word.language)
            if not loan.certain:
                yield ' (uncertain)'

    return HTML.ul(
        *[HTML.li(*list(_format(loan))) for loan in ctx.source_word_assocs],
        class_="unstyled")


def term_link(req, term, label=None):
    parts = term.split()
    if len(parts) > 1:
        # term contains white-space!
        label = label or term
        term = '_'.join(parts)
    else:
        label = label or term.replace('_', ' ')
    term = term.lower()
    return HTML.a(
        label,
        title="lookup '{0}' in the glossary".format(term.replace('_', ' ')),
        href=req.route_url('terms', _anchor=term))


def home_link(req, label=None):
    return HTML.a(
        label or req.dataset.description,
        title=req.dataset.description,
        href=req.resource_url(req.dataset))
