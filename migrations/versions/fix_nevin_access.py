
"""fix nevin access

Revision ID: fix_nevin_access
Create Date: 2024-01-04
"""
from alembic import op
import sqlalchemy as sa
from datetime import datetime, timedelta

revision = 'fix_nevin_access'
down_revision = None
branch_labels = None
depends_on = None

def upgrade():
    # Add nevin_access column if it doesn't exist
    op.execute("""
    DO $$
    BEGIN
        IF NOT EXISTS (SELECT 1 FROM information_schema.columns 
                      WHERE table_name='users' AND column_name='nevin_access') THEN
            ALTER TABLE users ADD COLUMN nevin_access BOOLEAN DEFAULT TRUE;
        END IF;
    END
    $$;
    """)

def downgrade():
    op.drop_column('users', 'nevin_access')
