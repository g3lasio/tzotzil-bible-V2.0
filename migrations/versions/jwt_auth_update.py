"""jwt auth update

Revision ID: jwt_auth_update
Revises: add_reset_fields
Create Date: 2025-01-02 10:00:00.000000

"""
from alembic import op
import sqlalchemy as sa

# revision identifiers
revision = 'jwt_auth_update'
down_revision = 'add_reset_fields'
branch_labels = None
depends_on = None

def upgrade():
    # Agregar nuevas columnas para JWT si no existen
    op.execute("""
        DO $$ 
        BEGIN 
            BEGIN
                ALTER TABLE users ADD COLUMN IF NOT EXISTS is_active BOOLEAN DEFAULT TRUE;
                ALTER TABLE users ADD COLUMN IF NOT EXISTS last_login TIMESTAMP WITH TIME ZONE;
                ALTER TABLE users ADD COLUMN IF NOT EXISTS password_hash VARCHAR(256) NOT NULL DEFAULT '';
            EXCEPTION WHEN duplicate_column THEN 
                NULL;
            END;
        END $$;
    """)

def downgrade():
    # No eliminamos columnas en downgrade para preservar datos
    pass