
"""update user id to uuid

Revision ID: update_user_id_to_uuid
Create Date: 2024-01-04 17:45:00.000000
"""
from alembic import op
import sqlalchemy as sa
import uuid

def upgrade():
    # Crear tabla temporal con nuevo tipo de ID
    op.execute("""
    CREATE TABLE users_new (
        id VARCHAR(36) PRIMARY KEY,
        username VARCHAR(80) UNIQUE NOT NULL,
        lastname VARCHAR(50) NOT NULL,
        phone VARCHAR(15) NOT NULL,
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
    )
    """)
    
    # Migrar datos existentes con nuevos UUIDs
    op.execute("""
    INSERT INTO users_new 
    SELECT uuid_generate_v4()::varchar, username, lastname, phone, email, 
           password_hash, is_active, created_at, nevin_access, trial_ends_at, 
           trial_started_at, plan_type, subscription_start, subscription_status
    FROM users
    """)
    
    # Reemplazar tabla anterior
    op.execute("DROP TABLE users CASCADE")
    op.execute("ALTER TABLE users_new RENAME TO users")
    
    # Recrear índices
    op.create_index('ix_users_email', 'users', ['email'], unique=True)
    op.create_index('ix_users_username', 'users', ['username'], unique=True)

def downgrade():
    pass
