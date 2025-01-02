
"""Add reset fields to users table

Revision ID: add_reset_fields
Revises: 8af10b95505c
Create Date: 2024-01-02 16:55:00.000000

"""
from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision = 'add_reset_fields'
down_revision = '8af10b95505c'
branch_labels = None
depends_on = None

def upgrade():
    op.add_column('users', sa.Column('reset_code', sa.String(6), nullable=True))
    op.add_column('users', sa.Column('reset_code_expires', sa.DateTime, nullable=True))

def downgrade():
    op.drop_column('users', 'reset_code')
    op.drop_column('users', 'reset_code_expires')
