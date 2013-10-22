from __future__ import unicode_literals
from datetime import date

from sqlalchemy import create_engine

from clld.scripts.util import initializedb, Data
from clld.db.meta import DBSession
from clld.db.models import common

from wold2 import models


DB = 'postgresql://robert@/wold'


def main(args):
    old_db = create_engine(DB)
    data = Data()

    #
    # migrate contributor table: complete
    #
    for row in old_db.execute("select * from contributor"):
        data.add(
            common.Contributor, row['id'],
            id=row['id'],
            name='%(firstname)s %(lastname)s' % row,
            url=row['homepage'],
            description=row['note'],
            email=row['email'],
            address=row['address'])
    data.add(
        common.Contributor, 'haspelmathmartin',
        id='haspelmathmartin',
        name="Martin Haspelmath",
        url="http://email.eva.mpg.de/~haspelmt/")
    DBSession.flush()

    dataset = common.Dataset(
        id='wold',
        name='WOLD',
        description='World Loanword Database',
        domain='wold.livingsources.org',
        published=date(2009, 8, 15),
        license='http://creativecommons.org/licenses/by-sa/3.0/',
        #license='http://creativecommons.org/licenses/by-nc-nd/2.0/de/deed.en',
        contact='wold@eva.mpg.de',
        jsondata={
            'license_icon': 'http://i.creativecommons.org/l/by-sa/3.0/88x31.png',
            'license_name': 'Creative Commons Attribution-ShareAlike 3.0 Unported License'})
            #'license_icon': 'http://wals.info/static/images/cc_by_nc_nd.png',
            #'license_name': 'Creative Commons Attribution-NonCommercial-NoDerivs 2.0 Germany'})
    DBSession.add(dataset)

    for i, editor in enumerate(['haspelmathmartin', 'tadmoruri']):
        common.Editor(dataset=dataset, contributor=data['Contributor'][editor], ord=i + 1)

    #
    # migrate semantic_field table: complete
    #
    for row in old_db.execute("select * from semantic_field"):
        kw = dict((key, row[key]) for key in ['id', 'name', 'description'])
        data.add(models.SemanticField, row['id'], **kw)

    #
    # migrate language table: complete
    # recipient flag is replaced by vocabulary_pk!
    #
    for row in old_db.execute("select * from language order by id"):
        kw = dict((key, row[key]) for key in [
            'fm_dl_id', 'name', 'latitude', 'longitude', 'wals_equivalent',
            'affiliation', 'family', 'genus', 'countries'])
        data.add(models.WoldLanguage, row['id'], id=str(row['id']), **kw)

    #
    # migrate language_code table: complete
    #
    for row in old_db.execute("select * from language_code"):
        _id = '%(type)s-%(code)s' % row
        data.add(common.Identifier, _id, id=_id, type=row['type'], name=row['code'])
    DBSession.flush()

    #
    # migrate language_code_language table: complete
    #
    for row in old_db.execute("select * from language_code_language"):
        _id = '%(type)s-%(code)s' % row
        data.add(common.LanguageIdentifier, '%s-%s' % (_id, row['language_id']),
            identifier_pk=data['Identifier'][_id].pk, language_pk=data['WoldLanguage'][row['language_id']].pk)
    DBSession.flush()

    #
    # migrate vocabulary table: complete
    #
    for row in old_db.execute("select * from vocabulary order by id"):
        jsondata = {}
        for key in row.keys():
            if key.startswith('fd_') or key in ['other_information', 'abbreviations']:
                jsondata[key] = row[key]
        vocab = data.add(
            models.Vocabulary, row['id'],
            id=str(row['id']), name=row['name'], color=row['color'], jsondata=jsondata)
        DBSession.flush()
        data['WoldLanguage'][row['language_id']].vocabulary_pk = vocab.pk
    DBSession.flush()

    #
    # migrate contact_situation and age tables: complete
    # contact situations and ages are unitdomainelements!
    #
    contact_situation = common.UnitParameter(id='cs', name='Contact Situation')
    age = common.UnitParameter(id='a', name='Age')

    DBSession.add(contact_situation)
    DBSession.add(age)
    DBSession.flush()

    for row in old_db.execute("select * from contact_situation"):
        if row['vocabulary_id'] is None:
            continue
        kw = dict((key, row[key]) for key in ['description', 'id', 'name'])
        kw['id'] = 'cs-%s' % kw['id']
        p = data.add(models.WoldUnitDomainElement, row['id'], **kw)
        p.vocabulary = data['Vocabulary'][row['vocabulary_id']]
        p.unitparameter_pk = contact_situation.pk

    for row in old_db.execute("select * from age"):
        id_ = '%(vocabulary_id)s-%(label)s' % row
        kw = dict((key, row[key]) for key in ['start_year', 'end_year'])
        p = data.add(models.WoldUnitDomainElement, id_, id='a-%s' % id_, name=row['label'],
                description=row['description'], jsondata=kw)
        p.vocabulary = data['Vocabulary'][row['vocabulary_id']]
        p.unitparameter_pk = age.pk

    #
    # migrate meaning table: complete
    #
    for row in old_db.execute("select * from meaning"):
        kw = dict((key, row[key]) for key in [
            'description', 'core_list', 'ids_code', 'typical_context', 'semantic_category'])
        p = data.add(
            models.Meaning, row['id'],
            id=row['id'].replace('.', '-'),
            name=row['label'],
            sub_code=row['id'].split('.')[1] if '.' in row['id'] else '',
            semantic_field=data['SemanticField'][row['semantic_field_id']],
            **kw)
        DBSession.flush()

        for field in ['french', 'spanish', 'german', 'russian']:
            DBSession.add(models.Translation(name=row[field], lang=field, meaning=p))

        for key in data['WoldLanguage']:
            lang = data['WoldLanguage'][key]
            data.add(
                common.ValueSet, '%s-%s' % (key, row['id']),
                id='%s-%s' % (key, row['id']),
                language=lang,
                contribution=lang.vocabulary,
                parameter=p)

    DBSession.flush()

    #
    # migrate word table:
    #
    word_to_vocab = {}
    for row in old_db.execute("select * from word"):
        word_to_vocab[row['id']] = row['vocabulary_id']
        kw = dict((key, row[key]) for key in ['id', 'age_score',
                                              'borrowed', 'borrowed_score',
                                              'analyzability', 'simplicity_score'])
        w = data.add(models.Word, row['id'], name=row['form'], description=row['free_meaning'], **kw)
        w.language = data['Vocabulary'][row['vocabulary_id']].language

        if row['age_label']:
            DBSession.add(common.UnitValue(
                id='%(id)s-a' % row,
                unit=w,
                unitparameter=age,
                unitdomainelement=data['WoldUnitDomainElement']['%(vocabulary_id)s-%(age_label)s' % row],
                contribution=data['Vocabulary'][row['vocabulary_id']]))

        if row['contact_situation_id'] and row['contact_situation_id'] != '9129144185487768':
            DBSession.add(common.UnitValue(
                id='%(id)s-cs' % row,
                unit=w,
                unitparameter=contact_situation,
                unitdomainelement=data['WoldUnitDomainElement'][row['contact_situation_id']],
                contribution=data['Vocabulary'][row['vocabulary_id']]))

    DBSession.flush()

    #
    # migrate word_meaning table: complete
    #
    for i, row in enumerate(old_db.execute("select * from word_meaning")):
        data.add(
            models.Counterpart, i,
            id=i,
            description='%(relationship)s (%(comment_on_relationship)s)' % row,
            name=data['Word'][row['word_id']].name,
            valueset=data['ValueSet']['%s-%s' % (word_to_vocab[row['word_id']], row['meaning_id'])],
            word = data['Word'][row['word_id']])
    DBSession.flush()

    #
    # migrate vocabulary_contributor table: complete
    #
    for row in old_db.execute("select * from vocabulary_contributor"):
        DBSession.add(common.ContributionContributor(
            ord=row['ordinal'],
            primary=row['primary'],
            contributor_pk=data['Contributor'][row['contributor_id']].pk,
            contribution_pk=data['Vocabulary'][row['vocabulary_id']].pk))

    DBSession.flush()

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

        new = data.add(models.Word, id_, id=id_, name=row['form'], description=row['meaning'])
        new.language = data['WoldLanguage'][row['language_id']]

    DBSession.flush()

    #
    # migrate word_source_word relations
    # TODO: should be modelled as UnitParameter!
    #
    j = 0
    for row in old_db.execute("select * from word_source_word"):
        sws = []
        for i in range(4):
            id_ = '%s-%s' % (row['source_word_id'], i+1)
            if id_ in data['Word']:
                sws.append(data['Word'][id_])
        if not sws:
            j += 1
            #print(row['source_word_id'])
            #raise ValueError(row['source_word_id'])

        for sw in sws:
            DBSession.add(models.Loan(
                source_word=sw, target_word=data['Word'][row['word_id']],
                relation=row['relationship'], certain=len(sws) == 1))

    print('%s source words not migrated' % j)


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


if __name__ == '__main__':
    initializedb(create=main, prime_cache=prime_cache)
