
"""Add missing user fields

Revision ID: fix_user_fields_v5
Revises: fix_users_table_v4
Create Date: 2024-01-04 08:10:00.000000

"""
from alembic import op
import sqlalchemy as sa

revision = 'fix_user_fields_v5'
down_revision = 'fix_users_table_v4'
branch_labels = None
depends_on = None

def upgrade():
    # Agregar nuevas columnas de manera segura
    op.execute("""
    DO $$ 
    BEGIN 
        BEGIN
            ALTER TABLE users ADD COLUMN lastname VARCHAR(50) NOT NULL DEFAULT '';
        EXCEPTION 
            WHEN duplicate_column THEN NULL;
        END;
        
        BEGIN
            ALTER TABLE users ADD COLUMN phone VARCHAR(15) NOT NULL DEFAULT '';
        EXCEPTION 
            WHEN duplicate_column THEN NULL;
        END;
    END $$;
    """)

def downgrade():
    op.drop_column('users', 'lastname')
    op.drop_column('users', 'phone')
