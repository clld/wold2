from __future__ import unicode_literals
import os
import sys
import transaction
from collections import defaultdict

from sqlalchemy import engine_from_config, create_engine

from pyramid.paster import (
    get_appsettings,
    setup_logging,
    )

from clld.db.meta import (
    DBSession,
    VersionedDBSession,
    Base,
)
from clld.db.models import common

from wold2 import models


VersionedDBSession = DBSession


DB = 'postgresql://robert@/wold'


def usage(argv):
    cmd = os.path.basename(argv[0])
    print('usage: %s <config_uri>\n'
          '(example: "%s development.ini")' % (cmd, cmd))
    sys.exit(1)


def main(argv=sys.argv):
    if len(argv) != 2:
        usage(argv)

    old_db = create_engine(DB)

    config_uri = argv[1]
    setup_logging(config_uri)
    settings = get_appsettings(config_uri)
    engine = engine_from_config(settings, 'sqlalchemy.')
    DBSession.configure(bind=engine)
    Base.metadata.create_all(engine)
    VersionedDBSession.configure(bind=engine)

    data = defaultdict(dict)

    def add(model, type_, key, **kw):
        new = model(**kw)
        data[type_][key] = new
        VersionedDBSession.add(new)
        return new

    with transaction.manager:
        #
        # migrate semantic_field table: complete
        #
        for row in old_db.execute("select * from semantic_field"):
            kw = dict((key, row[key]) for key in ['id', 'name', 'description'])
            add(models.SemanticField, 'semantic_field', row['id'], **kw)

        #
        # migrate language table: complete
        # recipient flag is replaced by vocabulary_pk!
        #
        for row in old_db.execute("select * from language order by id"):
            kw = dict((key, row[key]) for key in [
                'fm_dl_id', 'name', 'latitude', 'longitude', 'wals_equivalent',
                'affiliation', 'family', 'genus', 'countries'])
            lang = add(models.WoldLanguage, 'language', row['id'], id=str(row['id']), **kw)

        #
        # migrate language_code table: complete
        #
        for row in old_db.execute("select * from language_code"):
            _id = '%(type)s-%(code)s' % row
            add(common.Identifier, 'identifier', _id, id=_id, type=row['type'], name=row['code'])
        VersionedDBSession.flush()

        #
        # migrate language_code_language table: complete
        #
        for row in old_db.execute("select * from language_code_language"):
            _id = '%(type)s-%(code)s' % row
            add(common.LanguageIdentifier, 'language_identifier', '%s-%s' % (_id, row['language_id']),
                identifier_pk=data['identifier'][_id].pk, language_pk=data['language'][row['language_id']].pk)
        VersionedDBSession.flush()

        #
        # migrate contributor table: complete
        #
        for row in old_db.execute("select * from contributor"):
            add(common.Contributor, 'contributor', row['id'], id=row['id'],
                name='%(firstname)s %(lastname)s' % row, url=row['homepage'],
                description=row['note'], email=row['email'], address=row['address'])
        VersionedDBSession.flush()

        #
        # migrate vocabulary table: complete
        #
        for row in old_db.execute("select * from vocabulary order by id"):
            kw = dict((key, row[key]) for key in ['name', 'other_information', 'color', 'abbreviations'])
            vocab = add(models.Vocabulary, 'contribution', row['id'], id=str(row['id']), **kw)
            VersionedDBSession.flush()

            for key in row.keys():
                if key.startswith('fd_'):
                    VersionedDBSession.add(common.Contribution_data(object_pk=vocab.pk, key=key, value=row[key]))

            data['language'][row['language_id']].vocabulary_pk = vocab.pk
        VersionedDBSession.flush()

        #
        # migrate contact_situation and age tables: complete
        # contact situations and ages are unitdomainelements!
        #
        contact_situation = common.UnitParameter(id='cs', name='Contact Situation')
        age = common.UnitParameter(id='a', name='Age')

        VersionedDBSession.add(contact_situation)
        VersionedDBSession.add(age)
        VersionedDBSession.flush()

        for row in old_db.execute("select * from contact_situation"):
            if row['vocabulary_id'] is None:
                continue
            kw = dict((key, row[key]) for key in ['description', 'id', 'name'])
            kw['id'] = 'cs-%s' % kw['id']
            p = add(models.WoldUnitDomainElement, 'contact_situation', row['id'], **kw)
            p.vocabulary = data['contribution'][row['vocabulary_id']]
            p.unitparameter_pk = contact_situation.pk

        for row in old_db.execute("select * from age"):
            id_ = '%(vocabulary_id)s-%(label)s' % row
            kw = dict((key, row[key]) for key in ['start_year', 'end_year'])
            p = add(models.WoldUnitDomainElement, 'age', id_, id='a-%s' % id_, name=row['label'],
                    description=row['description'], jsondata=kw)
            p.vocabulary = data['contribution'][row['vocabulary_id']]
            p.unitparameter_pk = age.pk

        #
        # migrate meaning table: complete
        #
        for row in old_db.execute("select * from meaning"):
            kw = dict((key, row[key]) for key in [
                'description', 'core_list', 'ids_code', 'typical_context', 'semantic_category'])
            p = add(models.Meaning, 'parameter', row['id'], id=row['id'].replace('.', '-'), name=row['label'], **kw)
            p.semantic_field = data['semantic_field'][row['semantic_field_id']]

            for field in ['french', 'spanish', 'german', 'russian']:
                t = models.Translation(name=row[field], lang=field)
                t.meaning = p
                VersionedDBSession.add(t)
        VersionedDBSession.flush()

        #
        # migrate word table:
        #
        word_to_vocab = {}
        for row in old_db.execute("select * from word"):
            word_to_vocab[row['id']] = row['vocabulary_id']
            kw = dict((key, row[key]) for key in ['id', 'age_score',
                                                  'borrowed', 'borrowed_score',
                                                  'analyzability', 'simplicity_score'])
            w = add(models.Word, 'word', row['id'], name=row['form'], description=row['free_meaning'], **kw)
            w.language = data['contribution'][row['vocabulary_id']].language

            if row['age_label']:
                uv = common.UnitValue(id='%(id)s-a' % row)
                VersionedDBSession.add(uv)
                uv.unit = w
                uv.unitparameter = age
                uv.unitdomainelement = data['age']['%(vocabulary_id)s-%(age_label)s' % row]
                uv.contribution = data['contribution'][row['vocabulary_id']]

            if row['contact_situation_id'] and row['contact_situation_id'] != '9129144185487768':
                uv = common.UnitValue(id='%(id)s-cs' % row)
                VersionedDBSession.add(uv)
                uv.unit = w
                uv.unitparameter = contact_situation
                uv.unitdomainelement = data['contact_situation'][row['contact_situation_id']]
                uv.contribution = data['contribution'][row['vocabulary_id']]

        VersionedDBSession.flush()

        #
        # migrate word_meaning table: complete
        #
        for i, row in enumerate(old_db.execute("select * from word_meaning")):
            value = add(models.Counterpart, 'value', i, id=i,
                        description='%(relationship)s (%(comment_on_relationship)s)' % row,
                        name=data['word'][row['word_id']].name)
            value.parameter = data['parameter'][row['meaning_id']]
            value.language = data['contribution'][word_to_vocab[row['word_id']]].language
            value.contribution = data['contribution'][word_to_vocab[row['word_id']]]
            value.word = data['word'][row['word_id']]
        VersionedDBSession.flush()

        #
        # migrate vocabulary_contributor table: complete
        #
        for row in old_db.execute("select * from vocabulary_contributor"):
            new = common.ContributionContributor(
                ord=row['ordinal'],
                primary=row['primary'],
                contributor_pk=data['contributor'][row['contributor_id']].pk,
                contribution_pk=data['contribution'][row['vocabulary_id']].pk)
            VersionedDBSession.add(new)

        VersionedDBSession.flush()

        #
        # source words: we have to reassign identifier!
        #
        # loop over source_word, source_word_donor_language pairs keeping track of source_word ids:
        known_ids = {}

        for row in old_db.execute("select sw.id, sw.meaning, sw.form, dl.language_id from source_word as sw, source_word_donor_language as dl where sw.id = dl.source_word_id"):
            if row['id'] in known_ids:
                # source_word was already seen associated to a different donor language!
                assert row['language_id'] not in known_ids[row['id']]
                known_ids[row['id']].append(row['language_id'])
                id_ = '%s-%s' % (row['id'], len(known_ids[row['id']]))
            else:
                id_ = '%s-%s' % (row['id'], 1)
                known_ids[row['id']] = [row['language_id']]

            new = add(models.Word, 'source_word', id_, id=id_, name=row['form'], description=row['meaning'])
            new.language = data['language'][row['language_id']]
            VersionedDBSession.add(new)

        VersionedDBSession.flush()

        print(len(data['source_word']))

        #
        # migrate word_source_word relations
        # TODO: should be modelled as UnitParameter!
        #
        j = 0
        for row in old_db.execute("select * from word_source_word"):
            sws = []
            for i in range(4):
                id_ = '%s-%s' % (row['source_word_id'], i+1)
                if id_ in data['source_word']:
                    sws.append(data['source_word'][id_])
            if not sws:
                j += 1
                #print(row['source_word_id'])
                #raise ValueError(row['source_word_id'])

            for sw in sws:
                VersionedDBSession.add(models.Loan(
                    source_word=sw, target_word=data['word'][row['word_id']],
                    relation=row['relationship'], certain=len(sws) == 1))

        print('%s source words not migrated' % j)

        #
        # add precalculated scores for meanings and semantic fields:
        #
        for type_ in ['borrowed', 'age', 'simplicity']:
            attr = '%s_score' % type_

            for row in VersionedDBSession.execute(models.score_per_meaning_query(type_)):
                meaning = VersionedDBSession.query(models.Meaning).get(row['meaning_pk'])
                setattr(meaning, attr, row[attr])

            for row in VersionedDBSession.execute(models.score_per_semanticfield_query(type_)):
                sf = VersionedDBSession.query(models.SemanticField).get(row['semantic_field_pk'])
                setattr(sf, attr, row[1])

        VersionedDBSession.flush()


if __name__ == '__main__':
    main()
