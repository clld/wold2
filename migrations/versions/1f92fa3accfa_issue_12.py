# coding=utf-8
"""issue 12

Revision ID: 1f92fa3accfa
Revises: 4629bb75e715
Create Date: 2014-10-22 20:34:55.526907

"""

# revision identifiers, used by Alembic.
revision = '1f92fa3accfa'
down_revision = '4629bb75e715'

import datetime

from alembic import op
import sqlalchemy as sa


def upgrade():
    op.execute("create index on value (valueset_pk)")
    op.execute("create index on valuesetreference (valueset_pk)")
    op.execute("delete from valueset where language_pk > 41")


def downgrade():
    pass

