
"""merge: unify initial heads

Revision ID: 9f19a59fa239
Revises: 0001_initial, 2e3418fca3f1
Create Date: 2026-01-28 19:55:00.776377

"""

from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision = '9f19a59fa239'
down_revision = ('0001_initial', '2e3418fca3f1')
branch_labels = None
depends_on = None


def upgrade():
    pass


def downgrade():
    pass

