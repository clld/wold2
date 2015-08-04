# coding=utf-8
"""fix poly word

Revision ID: 28959d50de6
Revises: 207db8b425a8
Create Date: 2015-08-04 12:39:04.468959

"""

# revision identifiers, used by Alembic.
revision = '28959d50de6'
down_revision = '207db8b425a8'

import datetime

from alembic import op
import sqlalchemy as sa


def upgrade():
    update_pmtype(['unit'], 'base', 'custom')


def downgrade():
    update_pmtype(['unit'], 'custom', 'base')


def update_pmtype(tablenames, before, after):
    for table in tablenames:
        op.execute(sa.text('UPDATE %s SET polymorphic_type = :after '
            'WHERE polymorphic_type = :before' % table
            ).bindparams(before=before, after=after))

