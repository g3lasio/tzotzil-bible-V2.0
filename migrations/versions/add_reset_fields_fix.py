
"""add reset fields fix

Revision ID: add_reset_fields_fix
Revises: b95578ef4b5c
Create Date: 2024-01-02 18:30:00.000000

"""
from alembic import op
import sqlalchemy as sa

revision = 'add_reset_fields_fix'
down_revision = 'b95578ef4b5c'
branch_labels = None
depends_on = None

def upgrade():
    op.add_column('users', sa.Column('reset_code', sa.String(6), nullable=True))
    op.add_column('users', sa.Column('reset_code_expires', sa.DateTime(), nullable=True))

def downgrade():
    op.drop_column('users', 'reset_code')
    op.drop_column('users', 'reset_code_expires')
