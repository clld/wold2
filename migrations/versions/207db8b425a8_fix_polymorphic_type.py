# coding=utf-8
"""fix polymorphic_type

Revision ID: 207db8b425a8
Revises: 1f92fa3accfa
Create Date: 2014-11-26 16:13:41.792000

"""

# revision identifiers, used by Alembic.
revision = '207db8b425a8'
down_revision = '1f92fa3accfa'

import datetime

from alembic import op
import sqlalchemy as sa


def upgrade():
    update_pmtype(['unitdomainelement', 'value', 'contribution', 'language', 'parameter'],
        'base', 'custom')


def downgrade():
    update_pmtype(['unitdomainelement', 'value', 'contribution', 'language', 'parameter'],
        'custom', 'base')


def update_pmtype(tablenames, before, after):
    for table in tablenames:
        op.execute(sa.text('UPDATE %s SET polymorphic_type = :after '
            'WHERE polymorphic_type = :before' % table
            ).bindparams(before=before, after=after))
