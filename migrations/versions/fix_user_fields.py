
"""fix user fields

Revision ID: fix_user_fields
Revises: add_subscription_fields
Create Date: 2024-01-04 12:00:00.000000
"""
from alembic import op
import sqlalchemy as sa

revision = 'fix_user_fields'
down_revision = 'add_subscription_fields'
branch_labels = None
depends_on = None

def upgrade():
    # Agregar campos faltantes para el signup
    op.execute("""
    DO $$
    BEGIN
        IF NOT EXISTS (SELECT 1 FROM information_schema.columns 
                      WHERE table_name='users' AND column_name='lastname') THEN
            ALTER TABLE users ADD COLUMN lastname VARCHAR(50) NOT NULL DEFAULT '';
        END IF;
        
        IF NOT EXISTS (SELECT 1 FROM information_schema.columns 
                      WHERE table_name='users' AND column_name='phone') THEN
            ALTER TABLE users ADD COLUMN phone VARCHAR(15) NOT NULL DEFAULT '';
        END IF;
    END
    $$;
    """)

def downgrade():
    op.drop_column('users', 'lastname')
    op.drop_column('users', 'phone')
