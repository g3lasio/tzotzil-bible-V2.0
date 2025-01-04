
"""force add user fields

Revision ID: force_add_user_fields
Create Date: 2024-01-04 10:00:00.000000
"""
from alembic import op
import sqlalchemy as sa

revision = 'force_add_user_fields'
down_revision = None
branch_labels = None
depends_on = None

def upgrade():
    # Forzar la creación de las columnas
    op.execute("""
    DO $$ 
    BEGIN
        -- Intentar eliminar las columnas si existen
        BEGIN
            ALTER TABLE users DROP COLUMN IF EXISTS lastname;
            ALTER TABLE users DROP COLUMN IF EXISTS phone;
        EXCEPTION WHEN undefined_column THEN
            NULL;
        END;
        
        -- Crear las columnas
        BEGIN
            ALTER TABLE users ADD COLUMN lastname VARCHAR(50) NOT NULL DEFAULT '';
        EXCEPTION WHEN duplicate_column THEN
            ALTER TABLE users ALTER COLUMN lastname TYPE VARCHAR(50);
        END;
        
        BEGIN
            ALTER TABLE users ADD COLUMN phone VARCHAR(15) NOT NULL DEFAULT '';
        EXCEPTION WHEN duplicate_column THEN
            ALTER TABLE users ALTER COLUMN phone TYPE VARCHAR(15);
        END;
    END $$;
    """)

def downgrade():
    op.execute("""
    ALTER TABLE users DROP COLUMN IF EXISTS lastname;
    ALTER TABLE users DROP COLUMN IF EXISTS phone;
    """)
