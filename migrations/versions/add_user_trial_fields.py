
"""add user trial fields

Revision ID: add_user_trial_fields
Create Date: 2024-01-03
"""
from alembic import op
import sqlalchemy as sa

def upgrade():
    op.add_column('users', sa.Column('registered_at', sa.DateTime, server_default=sa.func.now()))
    op.add_column('users', sa.Column('nevin_access', sa.Boolean, server_default='true'))

def downgrade():
    op.drop_column('users', 'registered_at')
    op.drop_column('users', 'nevin_access')
