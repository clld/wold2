# coding=utf-8
"""fix wals genus urls

Revision ID: 2db9d56108eb
Revises: 13f7297e33ed
Create Date: 2015-10-09 09:33:37.769194

"""

# revision identifiers, used by Alembic.
revision = '2db9d56108eb'
down_revision = u'13f7297e33ed'

import datetime

from alembic import op
import sqlalchemy as sa


def upgrade():
    op.execute("update woldlanguage set genus = replace(genus, 'dev.livingreviews.org/wals', 'wals.info')")
    op.execute("update woldlanguage set family = replace(family, 'dev.livingreviews.org/wals', 'wals.info')")


def downgrade():
    pass
