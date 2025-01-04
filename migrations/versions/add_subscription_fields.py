"""add subscription fields

Revision ID: add_subscription_fields
Create Date: 2024-01-04 10:00:00.000000
"""
from alembic import op
import sqlalchemy as sa

revision = 'add_subscription_fields'
down_revision = 'init_schema'
branch_labels = None
depends_on = None

def upgrade():
    # Agregar campos de suscripción
    op.add_column('users', sa.Column('nevin_access', sa.Boolean(), server_default='true', nullable=False))
    op.add_column('users', sa.Column('trial_ends_at', sa.DateTime, nullable=True))
    op.add_column('users', sa.Column('trial_started_at', sa.DateTime, nullable=True))
    op.add_column('users', sa.Column('plan_type', sa.String(20), nullable=False, server_default='Free'))
    op.add_column('users', sa.Column('subscription_start', sa.DateTime, nullable=True))
    op.add_column('users', sa.Column('subscription_status', sa.String(20), nullable=False, server_default='inactive'))

def downgrade():
    op.drop_column('users', 'subscription_status')
    op.drop_column('users', 'subscription_start')
    op.drop_column('users', 'plan_type')
    op.drop_column('users', 'trial_started_at')
    op.drop_column('users', 'trial_ends_at')
    op.drop_column('users', 'nevin_access')