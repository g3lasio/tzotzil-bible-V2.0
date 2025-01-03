
"""Add trial period fields

Revision ID: add_trial_fields
Revises: b95578ef4b5c
Create Date: 2024-01-03 21:55:00.000000

"""
from alembic import op
import sqlalchemy as sa

# revision identifiers
revision = 'add_trial_fields'
down_revision = 'b95578ef4b5c'
branch_labels = None
depends_on = None

def upgrade():
    op.add_column('users', sa.Column('trial_end_date', sa.DateTime(), nullable=True))
    op.add_column('users', sa.Column('is_premium', sa.Boolean(), server_default='false', nullable=False))

def downgrade():
    op.drop_column('users', 'trial_end_date')
    op.drop_column('users', 'is_premium')
