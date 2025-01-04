
"""recreate users table with fields

Revision ID: recreate_users_table_with_fields
Create Date: 2024-01-04 12:00:00.000000
"""
from alembic import op
import sqlalchemy as sa

revision = 'recreate_users_table_with_fields'
down_revision = None
branch_labels = None
depends_on = None

def upgrade():
    # Crear tabla temporal con la estructura correcta
    op.execute("""
    CREATE TABLE users_new (
        id SERIAL PRIMARY KEY,
        username VARCHAR(80) UNIQUE NOT NULL,
        lastname VARCHAR(50) NOT NULL DEFAULT '',
        phone VARCHAR(15) NOT NULL DEFAULT '',
        email VARCHAR(120) UNIQUE NOT NULL,
        password_hash VARCHAR(256),
        is_active BOOLEAN DEFAULT TRUE,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        nevin_access BOOLEAN DEFAULT TRUE,
        trial_ends_at TIMESTAMP,
        trial_started_at TIMESTAMP,
        plan_type VARCHAR(20) DEFAULT 'Free' NOT NULL,
        subscription_start TIMESTAMP,
        subscription_status VARCHAR(20) DEFAULT 'inactive' NOT NULL
    );
    
    -- Copiar datos existentes
    INSERT INTO users_new (
        id, username, email, password_hash, is_active, 
        created_at, nevin_access, trial_ends_at, trial_started_at,
        plan_type, subscription_start, subscription_status
    )
    SELECT 
        id, username, email, password_hash, is_active,
        created_at, nevin_access, trial_ends_at, trial_started_at,
        plan_type, subscription_start, subscription_status
    FROM users;
    
    -- Eliminar tabla antigua y renombrar la nueva
    DROP TABLE users CASCADE;
    ALTER TABLE users_new RENAME TO users;
    
    -- Recrear índices
    CREATE INDEX ix_users_email ON users(email);
    CREATE INDEX ix_users_username ON users(username);
    """)

def downgrade():
    pass
