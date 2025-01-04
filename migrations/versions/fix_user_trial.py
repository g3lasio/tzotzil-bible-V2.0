
"""fix user trial

Revision ID: fix_user_trial
Revises: fix_auth_tables
Create Date: 2024-01-03 12:00:00.000000

"""
from alembic import op
import sqlalchemy as sa
from datetime import datetime, timedelta

revision = 'fix_user_trial'
down_revision = 'fix_auth_tables'
branch_labels = None
depends_on = None

def upgrade():
    # Eliminar columna registered_at si existe
    op.execute("ALTER TABLE users DROP COLUMN IF EXISTS registered_at")
    
    # Actualizar trial_ends_at para usuarios existentes
    op.execute("""
    UPDATE users 
    SET trial_ends_at = created_at + INTERVAL '30 days'
    WHERE trial_ends_at IS NULL
    """)

def downgrade():
    pass
