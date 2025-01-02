
"""Fix last_login field

Revision ID: fix_last_login_field
Revises: b95578ef4b5c
Create Date: 2024-12-31 16:30:00.000000
"""
from alembic import op
import sqlalchemy as sa

revision = 'fix_last_login_field'
down_revision = 'b95578ef4b5c'
branch_labels = None
depends_on = None

def upgrade():
    with op.batch_alter_table('users') as batch_op:
        batch_op.add_column(sa.Column('last_login', sa.DateTime(), nullable=True))

def downgrade():
    with op.batch_alter_table('users') as batch_op:
        batch_op.drop_column('last_login')
