
"""remove last_login column

Revision ID: remove_last_login
Revises: fix_auth_tables
Create Date: 2025-01-02 20:30:00.000000

"""
from alembic import op
import sqlalchemy as sa

revision = 'remove_last_login'
down_revision = 'fix_auth_tables'
branch_labels = None
depends_on = None

def upgrade():
    try:
        op.drop_column('users', 'last_login')
    except:
        pass

def downgrade():
    op.add_column('users', sa.Column('last_login', sa.DateTime(), nullable=True))
