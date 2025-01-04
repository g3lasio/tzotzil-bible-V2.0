
"""create user fields direct

Revision ID: create_user_fields_direct
Create Date: 2024-01-04 11:00:00.000000
"""
from alembic import op
import sqlalchemy as sa

revision = 'create_user_fields_direct'
down_revision = None
branch_labels = None
depends_on = None

def upgrade():
    # Usar SQL directo para agregar las columnas
    op.execute("""
    DO $$
    BEGIN
        BEGIN
            ALTER TABLE users ADD COLUMN IF NOT EXISTS lastname VARCHAR(50) DEFAULT '';
        EXCEPTION WHEN duplicate_column THEN
            NULL;
        END;
        
        BEGIN
            ALTER TABLE users ADD COLUMN IF NOT EXISTS phone VARCHAR(15) DEFAULT '';
        EXCEPTION WHEN duplicate_column THEN
            NULL;
        END;
        
        -- Asegurarse que las columnas tengan el tipo correcto
        ALTER TABLE users ALTER COLUMN lastname TYPE VARCHAR(50);
        ALTER TABLE users ALTER COLUMN phone TYPE VARCHAR(15);
        
        -- Asegurarse que las columnas no sean nulas
        ALTER TABLE users ALTER COLUMN lastname SET NOT NULL;
        ALTER TABLE users ALTER COLUMN phone SET NOT NULL;
        
        -- Establecer valores por defecto para registros existentes
        UPDATE users SET lastname = '' WHERE lastname IS NULL;
        UPDATE users SET phone = '' WHERE phone IS NULL;
    END;
    $$;
    """)

def downgrade():
    op.execute("""
    ALTER TABLE users DROP COLUMN IF EXISTS lastname;
    ALTER TABLE users DROP COLUMN IF EXISTS phone;
    """)
