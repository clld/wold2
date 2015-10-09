# coding=utf-8
"""fix glottocodes

See https://github.com/clld/wold-data/issues/2

Revision ID: 13f7297e33ed
Revises: 3001d8dfee6a
Create Date: 2015-10-09 09:18:10.963757

"""
from __future__ import unicode_literals

# revision identifiers, used by Alembic.
revision = '13f7297e33ed'
down_revision = '3001d8dfee6a'

from alembic import op

from clld.db.migration import Connection


def upgrade():
    conn = Connection(op.get_bind())
    conn.set_glottocode('19', 'yaku1245')  # Sakha
    conn.set_glottocode('11', 'oldh1241')  # Old High German
    conn.set_glottocode('9', 'west2376')  # Selice Romani
    conn.set_glottocode('17', 'mana1288')  # Manange


def downgrade():
    pass
