# coding=utf-8
"""contact email

Revision ID: 3001d8dfee6a
Revises: 28959d50de6
Create Date: 2015-10-07 11:06:19.588112

"""

# revision identifiers, used by Alembic.
revision = '3001d8dfee6a'
down_revision = '28959d50de6'

import datetime

from alembic import op
import sqlalchemy as sa


def upgrade():
    op.execute("update dataset set contact = 'wold@shh.mpg.de'")

def downgrade():
    pass

