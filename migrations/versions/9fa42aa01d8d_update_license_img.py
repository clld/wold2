# coding=utf-8
"""update license img

Revision ID: 9fa42aa01d8d
Revises: a3370476a21e
Create Date: 2018-08-14 11:57:31.922931

"""

# revision identifiers, used by Alembic.
revision = '9fa42aa01d8d'
down_revision = 'a3370476a21e'

import datetime

from alembic import op
import sqlalchemy as sa


def upgrade():
    op.execute("""\
UPDATE dataset SET jsondata = '{"license_name": "Creative Commons Attribution 3.0 Germany License", "license_icon": "cc-by.png"}'\
""")

def downgrade():
    pass

