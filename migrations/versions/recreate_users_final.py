
"""recreate users final

Revision ID: recreate_users_final
Create Date: 2024-01-04 15:00:00.000000
"""
from alembic import op
import sqlalchemy as sa

revision = 'recreate_users_final'
down_revision = None
branch_labels = None
depends_on = None

def upgrade():
    # Crear tabla temporal con todos los campos necesarios
    op.execute("""
    DROP TABLE IF EXISTS users CASCADE;
    CREATE TABLE users (
        id SERIAL PRIMARY KEY,
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
        subscription_status VARCHAR(20) DEFAULT 'inactive' NOT NULL,
        reset_code VARCHAR(6),
        reset_code_expires TIMESTAMP
    );
    
    -- Recrear índices
    CREATE INDEX ix_users_email ON users(email);
    CREATE INDEX ix_users_username ON users(username);
    
    -- Reiniciar la secuencia
    SELECT setval('users_id_seq', COALESCE((SELECT MAX(id) FROM users), 0) + 1, false);
    """)

def downgrade():
    op.drop_table('users')
