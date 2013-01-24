from zope.interface import implementer
from sqlalchemy import (
    Column,
    String,
    Unicode,
    Integer,
    Float,
    Boolean,
    ForeignKey,
    UniqueConstraint,
    and_,
    distinct,
)
from sqlalchemy.orm import relationship, backref
from sqlalchemy.ext.declarative import declared_attr
from sqlalchemy.ext.hybrid import hybrid_property
from sqlalchemy.sql import select, func
from sqlalchemy.sql.expression import cast, alias

from clld import interfaces
from clld.db.meta import Base, DBSession, CustomModelMixin
from clld.db.models.common import (
    Language,
    Parameter,
    Value,
    DomainElement,
    Contribution,
    Unit,
    UnitParameter,
    UnitDomainElement,
    IdNameDescriptionMixin,
)


class ScoreMixin(object):
    borrowed_score = Column(Float)
    age_score = Column(Float)
    simplicity_score = Column(Float)


class SemanticField(Base, IdNameDescriptionMixin, ScoreMixin):
    pass


@implementer(interfaces.IContribution)
class Vocabulary(Contribution, CustomModelMixin):
    pk = Column(Integer, ForeignKey('contribution.pk'), primary_key=True)

    other_information = Column(Unicode)
    color = Column(String(6))  # three letter hex rgb values
    abbreviations = Column(Unicode)


@implementer(interfaces.IUnitDomainElement)
class WoldUnitDomainElement(UnitDomainElement, CustomModelMixin):
    """In WOLD, most unit parameters (like contact situation or age) have vocabulary
    specific domains. Thus we store a reference to the vocabulary.
    """
    pk = Column(Integer, ForeignKey('unitdomainelement.pk'), primary_key=True)
    vocabulary_pk = Column(Integer, ForeignKey('vocabulary.pk'))
    vocabulary = relationship(Vocabulary)


@implementer(interfaces.IUnit)
class Word(Unit, ScoreMixin):
    pk = Column(Integer, ForeignKey('unit.pk'), primary_key=True)
    #vocabulary_id = Column(Integer, ForeignKey('vocabulary.id'))

    #
    # TODO: turn the relations below into UnitValue
    #
    #contact_situation_pk = Column(Integer, ForeignKey('contactsituation.pk'))
    #age_pk = Column(Integer, ForeignKey('age.pk'))

    #contact_situation = relationship(ContactSituation, backref='words')
    #age = relationship(Age, backref='words')

#    form = Column(Unicode) -> name
#    free_meaning = Column(Unicode) -> description

    #
    # TODO: the following are Unit Parameter values!
    #
    borrowed = Column(Unicode)
    analyzability = Column(Unicode)


class Loan(Base):
    relation = Column(Unicode)
    certain = Column(Boolean, default=True)

    target_word_pk = Column(Integer, ForeignKey('word.pk'))
    target_word = relationship(Word, backref='source_word_assocs',
                               primaryjoin="Loan.target_word_pk==Word.pk")

    source_word_pk = Column(Integer, ForeignKey('word.pk'))
    source_word = relationship(Word, backref='target_word_assocs',
                               primaryjoin="Loan.source_word_pk==Word.pk")


@implementer(interfaces.IValue)
class Counterpart(Value, CustomModelMixin):
    """one row in what used to be the word-meaning association table
    """
    pk = Column(Integer, ForeignKey('value.pk'), primary_key=True)

    word_pk = Column(Integer, ForeignKey('word.pk'))
    word = relationship(Word, backref='counterparts')


@implementer(interfaces.ILanguage)
class WoldLanguage(Language, CustomModelMixin):
    pk = Column(Integer, ForeignKey('language.pk'), primary_key=True)
    vocabulary_pk = Column(Integer, ForeignKey('vocabulary.pk'))
    vocabulary = relationship(Vocabulary, backref=backref('language', uselist=False))

    fm_dl_id = Column(String)
    wals_equivalent = Column(String, default=None)
    affiliation = Column(Unicode, default=None)
    family = Column(String, default=None) # URL for genus in WALS
    genus = Column(String, default=None) # URL for family in WALS
    countries = Column(Unicode, default=None)


@implementer(interfaces.IParameter)
class Meaning(Parameter, CustomModelMixin, ScoreMixin):
    pk = Column(Integer, ForeignKey('parameter.pk'), primary_key=True)

    semantic_field_pk = Column(Integer, ForeignKey('semanticfield.pk'))
    semantic_field = relationship(SemanticField, backref='meanings')

    semantic_category = Column(Unicode)

    ids_code = Column(String)
    typical_context = Column(Unicode)
    #Column('french', Unicode())
    #Column('spanish', Unicode())
    #Column('german', Unicode())
    #Column('russian', Unicode())
    core_list = Column(Boolean)


    Column('french', Unicode()),
    Column('spanish', Unicode()),
    Column('german', Unicode()),
    Column('russian', Unicode()),
    Column('core_list', Boolean()),


class Translation(Base):
    meaning_pk = Column(Integer, ForeignKey('meaning.pk'))
    name = Column(Unicode)
    lang = Column(Unicode)
    meaning = relationship(Meaning, backref='translations')


def score_per_meaning_query(type_, filter_=None):
    """
select
    a.id, a.label, a.semantic_category, a.semantic_field_id, sum(a.borrowed_score)/sum(a.representation) as borrowed_score, count(distinct a.word_id)
from
(
    -- tabulate (word_id, meaning_id) pairs against a word's discounted score

    select
        x.word_id, x.meaning_id as id, x.label as label, x.semantic_field_id as semantic_field_id, x.semantic_category as semantic_category, y.borrowed_score, y.representation
    from
    (
        select wm.word_id as word_id, m.id as meaning_id, m.label as label, m.semantic_field_id as semantic_field_id, m.semantic_category as semantic_category
        from word_meaning as w+
    ) as x,
    --
    -- tabulate word ids against score discounted by number of meanings
    --
    (
        select
            w.pk as word_pk, w.id as word_id, cast(w.borrowed_score as float)/count(*) as borrowed_score, cast(1 as float)/count(*) as representation
        from
            word as w, counterpart as wm
        where
            w.pk = wm.word_pk
        group by
            w.id, w.borrowed_score
    ) as y
    -- ---------------------------------------------------------------------------
    where x.word_id = y.word_id
) as a --,
-- ---------------------------------------------------------------------------
-- select words we are interested in
--

group by
    a.label, a.id, a.semantic_category, a.semantic_field_id
order by
    a.id
    """
    assert type_ in ['borrowed', 'age', 'simplicity']
    attr = '%s_score' % type_

    word, counterpart, parameter, meaning, value = map(
        lambda mapper: mapper.__table__,
        [Word, Counterpart, Parameter, Meaning, Value])

    x = alias(
        select(
            [
                counterpart.c.word_pk.label('word_pk'),
                parameter.c.pk.label('meaning_pk'),
                meaning.c.semantic_field_pk.label('semantic_field_pk'),
            ],
            from_obj=value,
            whereclause=and_(
                value.c.parameter_pk == parameter.c.pk,
                parameter.c.pk == meaning.c.pk,
                value.c.pk == counterpart.c.pk)),
        name='x')

    y = alias(
        select(
            [
                word.c.pk.label('word_pk'),
                (cast(getattr(word.c, attr), Float)/func.count('*')).label(attr),
                (cast(1, Float)/func.count('*')).label('representation'),
            ],
            from_obj=counterpart,
            whereclause=word.c.pk == counterpart.c.word_pk,
            group_by=[word.c.pk, getattr(word.c, attr)],
        ),
        name='y')

    a = alias(
        select(
            [
                x.c.meaning_pk,
                x.c.semantic_field_pk,
                getattr(y.c, attr),
                y.c.representation
            ],
            whereclause=x.c.word_pk == y.c.word_pk),
        name='a')

    query = select(
        [
            a.c.meaning_pk,
            a.c.semantic_field_pk,
            (func.sum(getattr(a.c, attr))/func.sum(a.c.representation)).label(attr),
            func.count(distinct(a.c.meaning_pk)),
        ],
        group_by=[a.c.meaning_pk, a.c.semantic_field_pk],
        order_by=a.c.meaning_pk)

    if isinstance(filter_, Meaning):
        query = query.where(a.c.meaning_pk == filter_.pk)

    if isinstance(filter_, SemanticField):
        query = query.where(a.c.semantic_field_pk == filter_.pk)

    return query


def score_per_semanticfield_query(type_):
    aa = alias(score_per_meaning_query(type_), name='aa')

    return select(
        [
            aa.c.semantic_field_pk,
            func.sum(getattr(aa.c, '%s_score' % type_))/func.count('*'),
            func.count('*'),
        ],
        group_by=[aa.c.semantic_field_pk]
    )
