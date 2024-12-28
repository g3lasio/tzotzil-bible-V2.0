"""Add Nevin access fields

Revision ID: add_nevin_fields
Revises: 8af10b95505c
Create Date: 2024-12-03 14:45:00.000000

"""
from alembic import op
import sqlalchemy as sa
from datetime import datetime

# revision identifiers, used by Alembic.
revision = 'add_nevin_fields'
down_revision = '8af10b95505c'
branch_labels = None
depends_on = None

def upgrade():
    # Add nevin_access_days and is_premium columns with safe defaults
    op.add_column('users', sa.Column('nevin_access_days', sa.Integer(), nullable=False, server_default='0'))
    op.add_column('users', sa.Column('is_premium', sa.Boolean(), nullable=False, server_default='0'))

def downgrade():
    # Remove the columns
    op.drop_column('users', 'nevin_access_days')
    op.drop_column('users', 'is_premium')
