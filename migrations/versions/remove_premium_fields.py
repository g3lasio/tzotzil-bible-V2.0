
"""remove premium fields

Revision ID: remove_premium_fields
Create Date: 2024-01-05
"""
from alembic import op
import sqlalchemy as sa

revision = 'remove_premium_fields'
down_revision = 'add_subscription_fields'
branch_labels = None
depends_on = None

def upgrade():
    # Eliminar columnas relacionadas con premium y trial
    op.drop_column('users', 'trial_ends_at')
    op.drop_column('users', 'trial_started_at')
    op.drop_column('users', 'plan_type')
    op.drop_column('users', 'subscription_start')
    op.drop_column('users', 'subscription_status')

def downgrade():
    # Agregar columnas si es necesario revertir
    op.add_column('users', sa.Column('trial_ends_at', sa.DateTime, nullable=True))
    op.add_column('users', sa.Column('trial_started_at', sa.DateTime, nullable=True))
    op.add_column('users', sa.Column('plan_type', sa.String(20), nullable=False, server_default='Free'))
    op.add_column('users', sa.Column('subscription_start', sa.DateTime, nullable=True))
    op.add_column('users', sa.Column('subscription_status', sa.String(20), nullable=False, server_default='inactive'))
