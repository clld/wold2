# coding=utf-8
"""domain switch

Revision ID: 4629bb75e715
Revises: None
Create Date: 2014-06-04 09:34:36.604456

"""

# revision identifiers, used by Alembic.
revision = '4629bb75e715'
down_revision = None

import datetime

from alembic import op
import sqlalchemy as sa


def upgrade():
    op.execute("update dataset set domain = 'wold.clld.org';")


def downgrade():
    op.execute("update dataset set domain = 'wold.livingsources.org';")
