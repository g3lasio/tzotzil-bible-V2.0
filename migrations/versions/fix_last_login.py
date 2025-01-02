
"""Fix last_login field

Revision ID: fix_last_login_field
Revises: b95578ef4b5c
Create Date: 2024-01-02 20:30:00.000000
"""
from alembic import op
import sqlalchemy as sa

revision = 'fix_last_login_field'
down_revision = 'b95578ef4b5c'
branch_labels = None
depends_on = None

def upgrade():
    op.execute("""
    DO $$
    BEGIN
        IF NOT EXISTS (SELECT 1 FROM information_schema.columns 
                      WHERE table_name='users' AND column_name='last_login') THEN
            ALTER TABLE users ADD COLUMN last_login TIMESTAMP;
        END IF;
    END
    $$;
    """)

def downgrade():
    op.execute("ALTER TABLE users DROP COLUMN IF EXISTS last_login;")
