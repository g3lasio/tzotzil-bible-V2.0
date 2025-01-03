
"""add user trial fields

Revision ID: add_user_trial_fields_fix
Revises: 
Create Date: 2024-01-03
"""
from alembic import op
import sqlalchemy as sa

# revision identifiers
revision = 'add_user_trial_fields_fix'
down_revision = None
branch_labels = None
depends_on = None

def upgrade():
    # Agregar las columnas faltantes
    op.add_column('users', sa.Column('registered_at', sa.DateTime(), server_default=sa.func.now()))
    op.add_column('users', sa.Column('nevin_access', sa.Boolean(), server_default='true'))

def downgrade():
    op.drop_column('users', 'registered_at')
    op.drop_column('users', 'nevin_access')
