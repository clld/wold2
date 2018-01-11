# coding=utf-8
"""update unitdomainelement.name

Revision ID: e12a26fbba48
Revises: ebac95201589
Create Date: 2018-01-11 14:13:36.907213

"""
from __future__ import unicode_literals

# revision identifiers, used by Alembic.
revision = 'e12a26fbba48'
down_revision = 'ebac95201589'

import datetime

from alembic import op
import sqlalchemy as sa


def upgrade():
    conn = op.get_bind()
    udes = []
    for row in conn.execute("select pk, name from unitdomainelement"):
        udes.append((row[0], row[1]))

    for pk, name in udes:
        for row in conn.execute("select c.id from contribution as c, woldunitdomainelement as wude where c.pk = wude.vocabulary_pk and wude.pk = %s" % pk):
            vid = row[0]
            break
        else:
            raise ValueError
        nname = '{0} [{1}]'.format(name, vid)
        conn.execute("update unitdomainelement set name = %s where pk = %s", (nname, pk))


def downgrade():
    pass

