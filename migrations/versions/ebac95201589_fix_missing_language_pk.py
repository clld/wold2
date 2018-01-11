# coding=utf-8
"""fix missing language_pk

Revision ID: ebac95201589
Revises: 2db9d56108eb
Create Date: 2018-01-11 13:32:48.969652

"""

# revision identifiers, used by Alembic.
revision = 'ebac95201589'
down_revision = '2db9d56108eb'

import datetime

from alembic import op
import sqlalchemy as sa


def upgrade():
    conn = op.get_bind()
    for row in conn.execute("select pk from language where name = 'Unidentified'"):
        lpk = row[0]
        break
    else:
        raise ValueError
    conn.execute("update unit set language_pk = %s where language_pk is null" % lpk)

def downgrade():
    pass

