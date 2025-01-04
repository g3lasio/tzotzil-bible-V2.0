
"""update user trial fields

Revision ID: update_user_trial_fields
Revises: fix_auth_tables
Create Date: 2024-01-03 15:00:00.000000

"""
from alembic import op
import sqlalchemy as sa
from datetime import datetime

revision = 'update_user_trial_fields'
down_revision = 'fix_auth_tables'
branch_labels = None
depends_on = None

def upgrade():
    op.add_column('users', sa.Column('trial_started_at', sa.DateTime(), nullable=True))
    op.execute("UPDATE users SET trial_started_at = NOW() WHERE trial_started_at IS NULL")

def downgrade():
    op.drop_column('users', 'trial_started_at')
