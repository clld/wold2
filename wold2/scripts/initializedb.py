"""
Recreate the data import from CLDF data (as far as possible)
"""
import json
import itertools
import collections
import re
from datetime import date

from clld.db.meta import DBSession
from clld.db.models import common
from clld.cliutil import Data
from clld.web.util.helpers import text2html
from csvw.dsv import reader
from clld_glottologfamily_plugin.util import load_families
from pycldf.media import MediaTable
from clldutils.markup import iter_markdown_sections
from clldutils.html import HTML

from wold2 import models


def desc2html(s):
    def _iter_tr():
        for level, header, text in iter_markdown_sections(s):
            if level > 1:
                yield HTML.tr(HTML.th(header.lstrip('#').strip()), HTML.td(text2html(text)))
    return str(HTML.table(HTML.tbody(*list(_iter_tr())), class_='table table-condensed'))


def main(args):
    data = Data()
    db_dir = args.cldf.directory.parent / 'raw' / 'db'

    for row in args.cldf.iter_rows('contributors.csv'):
        data.add(common.Contributor, row['ID'], id=row['ID'], name=row['Name'], address=row['address'])
    DBSession.flush()

    dataset = common.Dataset(
        id='wold',
        name='WOLD',
        description='World Loanword Database',
        domain='wold.clld.org',
        published=date(2009, 8, 15),
        license='http://creativecommons.org/licenses/by/3.0/de/',
        contact='wold@eva.mpg.de',
        jsondata={
            'license_icon': 'http://i.creativecommons.org/l/by/3.0/de/88x31.png',
            'license_name': 'Creative Commons Attribution 3.0 Germany License'})
    DBSession.add(dataset)

    for i, editor in enumerate(['haspelmathmartin', 'tadmoruri']):
        common.Editor(dataset=dataset, contributor=data['Contributor'][editor], ord=i + 1)

    id2wold_id = {}
    for row in args.cldf.iter_rows('LanguageTable', 'id', 'name', 'latitude', 'longitude', 'glottocode'):
        kw = dict((key, row[key]) for key in ['name', 'latitude', 'longitude', 'glottocode'])
        id2wold_id[row['id']] = row['WOLD_ID']
        data.add(models.WoldLanguage, row['WOLD_ID'], id=str(row['WOLD_ID']), **kw)

    name2wold_id = {}
    for row in reader(args.cldf.directory.parent / 'etc' / 'languages.csv', dicts=True):
        if row['WOLD_ID'] not in data['WoldLanguage']:
            data.add(
                models.WoldLanguage, row['WOLD_ID'],
                id=row['WOLD_ID'],
                name=row['Name'],
                latitude=row['Latitude'] or None,
                longitude=row['Longitude'] or None,
                glottocode=row['Glottocode'] or None,
            )
        name2wold_id[row['Name']] = row['WOLD_ID']

    load_families(
        Data(),
        [(l.glottocode, l) for l in data['WoldLanguage'].values()],
        glottolog_repos=args.glottolog,
        isolates_icon='tcccccc',
        strict=False,
    )
    colors = {r['pk']: r['color'] for r in reader(db_dir / 'vocabulary.csv', dicts=True)}
    descs = {f.id: f for f in MediaTable(args.cldf)}
    # also: count_words,borrowed_score,count_core_list_counterparts
    #
    for row in args.cldf.iter_rows('ContributionTable', 'id'):
        vocab = data.add(
            models.Vocabulary, row['id'],
            id=str(row['ID']),
            name=row['Name'],
            description=desc2html(descs[row['ID']].read()),
            color=colors[row['ID']],
        )
        DBSession.flush()
        data['WoldLanguage'][row['id']].vocabulary_pk = vocab.pk
        for ctype in ['primary_contributors', 'secondary_contributors']:
            for i, cid in enumerate(row[ctype], start=1):
                DBSession.add(common.ContributionContributor(
                    ord=i,
                    primary=ctype.startswith('primary'),
                    contributor_pk=data['Contributor'][cid].pk,
                    contribution_pk=vocab.pk))

    DBSession.flush()

    contact_situation = common.UnitParameter(id='cs', name='Contact Situation')
    age = common.UnitParameter(id='a', name='Age')
    DBSession.add(contact_situation)
    DBSession.add(age)
    DBSession.flush()

    forms_by_language = collections.defaultdict(list)
    for form in args.cldf.iter_rows('FormTable'):
        forms_by_language[form['Language_ID']].append(form)

    udes = {}
    for r in reader(db_dir / 'unitdomainelement.csv', dicts=True):
        # name is unique if the following two are excluded:
        #pk,jsondata,id,name,description,markup_description,unitparameter_pk,ord,version
        #261,,cs-9129144493042350,No information [1],,,1,,1
        #1501,"{""start_year"": null, ""end_year"": null}",a-1-No information,No information [1],,,2,,1
        #
        # and matches contact_situation in cldf/forms.csv!
        # Age in cldf/forms.csv needs " [<lid>]" appended for lookup.
        if not r['name'].startswith('No information'):
            assert r['name'] not in udes
            udes[r['name']] = r

    f2ud = collections.defaultdict(dict)
    for lid, forms in forms_by_language.items():
        for up, col, pk in [(contact_situation, 'contact_situation', '1'), (age, 'Age', '2')]:
            for de, rows in itertools.groupby(
                sorted(forms, key=lambda r: r[col] or ''),
                lambda r: r[col],
            ):
                if not de:
                    continue
                if de.startswith('No information'):
                    continue
                if col == 'Age':
                    de = f'{de} [{id2wold_id[lid]}]'
                assert de in udes, de
                ude = udes[de]
                kw = dict((key, ude[key]) for key in ['description', 'id', 'name'])
                if col == 'Age':
                    kw['jsondata'] = json.loads(ude['jsondata'])

                kw['id'] = re.sub(r'\.\s+', '', kw['id'])
                p = data.add(models.WoldUnitDomainElement, de, **kw)
                p.vocabulary = data['Vocabulary'][id2wold_id[lid]]
                p.unitparameter_pk = up.pk

                for row in rows:
                    f2ud[row['ID']][col] = de

    meanings = {r['id']: r for r in reader(db_dir / 'parameter.csv', dicts=True)}
    m_by_pk = {r['pk']: r for r in meanings.values()}
    #borrowed_score,age_score,simplicity_score,
    # pk,semantic_field_pk,representation, semantic_category, sub_code, typical_context, core_list
    for row in reader(db_dir / 'meaning.csv', dicts=True):
        m_by_pk[row['pk']].update(row)
    for row in reader(db_dir / 'translation.csv', dicts=True):
        m_by_pk[row['meaning_pk']][row['lang']] = row['name']
    #
    # sub_code: used for ordering!
    #
    # ID, Name, Concepticon_ID, Concepticon_Gloss, Core_list, Semantic_category, Semantic_field
    for sf, rows in itertools.groupby(
            sorted(args.cldf.iter_rows('ParameterTable'), key=lambda r: r['Semantic_field']),
            lambda r: r['Semantic_field']
    ):
        for i, row in enumerate(rows):
            meaning = meanings[row['ID']]
            id_ = row['ID'].split('-')[0]
            if i == 0:
                sf = data.add(models.SemanticField, id_, id=id_, name=sf)
            kw = dict((key.lower(), row[key]) for key in [
                # description and context is also available from the Concepticon list
                #'description',  # ../wold/raw/db/parameter.csv -> description
                'Core_list',
                'Borrowed_score', 'Age_score', 'Simplicity_score',
                #'typical_context',  # ../wold/raw/db/meaning.csv -> typical_context
                'Semantic_category'])
            p = data.add(
                models.Meaning, row['ID'],
                id=row['ID'].replace('.', '-'),
                sfid=int(row['ID'].split('-')[0]),
                name=row['Name'],
                description=meaning['description'],
                typical_context=meaning['typical_context'],
                sub_code=meaning['sub_code'],
                semantic_field=sf,
                **kw)
            DBSession.flush()

            for field in ['french', 'spanish', 'german', 'russian']:
                DBSession.add(models.Translation(name=meaning[field], lang=field, meaning=p))

            for key in data['WoldLanguage']:
                lang = data['WoldLanguage'][key]
                data.add(
                    common.ValueSet, '%s-%s' % (key, row['ID']),
                    id='%s-%s' % (key, row['ID'].replace('.', '-')),
                    language=lang,
                    contribution=lang.vocabulary,
                    parameter=p)

    DBSession.flush()

    #
    # migrate word table:
    # TODO: all the other word properties!!
    #ID,
    # Local_ID,
    # Language_ID,
    # Parameter_ID,
    # Value,
    # Form,
    # Segments,
    # Source,
    # Loan,Graphemes,Profile,
    # Word_ID,
    unit_data = {r['id']: r for r in reader(db_dir / 'unit.csv', dicts=True)}
    for v in unit_data.values():
        v['jsondata'] = json.loads(v['jsondata'] or "{}")

    # contact_situation,
    fields_from_FormTable = {  # Mostly fields in ./db/unit.csv -> jsondata!
        'Age': 'age_label',
        'original_script': 'original_script',
        'grammatical_info': 'grammatical_info',
        'comment_on_word_form': 'comment_on_word_form',
        'gloss': 'gloss',
        'comment_on_borrowed': "comment_on_borrowed",
        'calqued': "calqued",
        'borrowed_base': "borrowed_base",
        'numeric_frequency': "numeric_frequency",
        'relative_frequency': "relative_frequency",
        'effect': "effect",
        'integration': "integration",
        'salience': "salience",
        'reference': "reference",
        'Comment': "other_comments",
        'register': "register",
        'loan_history': "loan_history",
        'colonial_word': 'colonial_word',
        'word_source': 'word_source',
        'lexical_stratum': 'lexical_stratum',
        'etymological_note': 'etymological_note',

        #'paraphrase_in_dutch',
        #'comparison_with_mandarin',
        #'year',
        #'paraphrase_in_german',
        #'comparison_with_korean',
        #'czech_translation',
        #'hungarian_translation',
        #'early_romani_reconstruction',
        #'boretzky_and_igla_etymology',
        #'manuss_et_al_etymology',
        #'vekerdi_etymology',
        #'turner_etymology',
        #'other_etymologies',
        #'mayrhofer_etymology',
    }
    words_by_word_id = {}

    for row in args.cldf.iter_rows('FormTable'):
        # Note: FormTable lists the form-meaning pairs in WOLD. But "words" in vocabularies
        # may correspond to multiple meanings. Thus, we must add words based on Word_ID.
        kw = dict((key.lower(), row[key]) for key in [
            'Age_score', 'Borrowed', 'Borrowed_score', 'Analyzability', 'Simplicity_score'])
        w = words_by_word_id.get(row['Word_ID'])
        if w:
            data['Word'][row['ID']] = w
        else:
            w = data.add(
                models.Word, row['ID'],
                id=row['Word_ID'],
                name=row['Value'],  # FormTable -> Value
                description=unit_data[row['Word_ID']]['description'],
                jsondata={v: row[k] for k, v in fields_from_FormTable.items()},
                **kw)
            w.language = data['WoldLanguage'][id2wold_id[row['Language_ID']]]
            if row['Age']:
                de = f"{row['Age']} [{id2wold_id[row['Language_ID']]}]"
                DBSession.add(common.UnitValue(
                    id='%(ID)s-a' % row,
                    unit=w,
                    unitparameter=age,
                    unitdomainelement=data['WoldUnitDomainElement'][de],
                    contribution=data['Vocabulary'][id2wold_id[row['Language_ID']]]))

            if row['contact_situation']:
                if not row['contact_situation'].startswith('No information'):
                    DBSession.add(common.UnitValue(
                        id='%(ID)s-cs' % row,
                        unit=w,
                        unitparameter=contact_situation,
                        unitdomainelement=data['WoldUnitDomainElement'][row['contact_situation']],
                        contribution=data['Vocabulary'][id2wold_id[row['Language_ID']]]))

        words_by_word_id[row['Word_ID']] = w

        # migrate word_meaning table: complete
        data.add(
            models.Counterpart, row['ID'],
            id=row['ID'],
            # FIXME: from value.csv -> description .replace("()", "").strip()
            #description='%(relationship)s (%(comment_on_relationship)s)' % row,
            name=w.name,
            valueset=data['ValueSet']['%s-%s' % (id2wold_id[row['Language_ID']], row['Parameter_ID'])],
            word=w)
    DBSession.flush()

    #
    # source words: we have to make sure a word does only belong to one language.
    # thus, we have to reassign identifier!
    # BorrowingTable
    #ID,Target_Form_ID,Comment,Source,
    # Source_relation,Source_word,Source_meaning,Source_certain,Source_languoid,Source_languoid_glottocode
    seen = set()
    for row in args.cldf.iter_rows('BorrowingTable'):
        key = (data['Word'][row['Target_Form_ID']].id, row['Source_relation'], row['Source_languoid'])
        if key in seen:
            continue
        seen.add(key)
        sw = data.add(
            models.Word, row['ID'],
            id=row['ID'],
            name=row['Source_word'] or 'Unidentifiable',
            description=row['Source_meaning'],
            language=data['WoldLanguage'][name2wold_id[row['Source_languoid']]],
        )
        DBSession.add(models.Loan(
            source_word=sw,
            target_word=data['Word'][row['Target_Form_ID']],
            relation=row['Source_relation'], certain=row['Source_certain']))

    DBSession.flush()
    return


def prime_cache(args):
    #
    # add precalculated scores for meanings and semantic fields:
    #
    for vocab in DBSession.query(models.Vocabulary):
        words = DBSession.query(models.Word.borrowed_score)\
            .join(common.Unit.language)\
            .join(models.WoldLanguage.vocabulary)\
            .filter(models.Vocabulary.pk == vocab.pk)\
            .filter(models.Word.borrowed_score != None)
        vocab.count_words = words.count()

        vocab.borrowed_score = sum(score[0] for score in words) / float(vocab.count_words)
        vocab.count_core_list_counterparts = DBSession.query(models.Counterpart)\
            .join(common.Value.valueset)\
            .join(common.ValueSet.parameter)\
            .filter(common.ValueSet.contribution_pk == vocab.pk)\
            .filter(models.Meaning.core_list == True)\
            .count()

    for meaning in DBSession.query(models.Meaning):
        meaning.representation = DBSession.query(models.Counterpart)\
            .join(common.ValueSet)\
            .filter(common.ValueSet.parameter_pk == meaning.pk)\
            .count()

    for type_ in ['borrowed', 'age', 'simplicity']:
        attr = '%s_score' % type_

        for row in DBSession.execute(models.score_per_meaning_query(type_)):
            meaning = DBSession.query(models.Meaning).get(row['meaning_pk'])
            setattr(meaning, attr, row[attr])

        for row in DBSession.execute(models.score_per_semanticfield_query(type_)):
            sf = DBSession.query(models.SemanticField).get(row['semantic_field_pk'])
            setattr(sf, attr, row[1])
