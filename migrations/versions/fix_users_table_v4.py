
"""fix users table v4

Revision ID: fix_users_table_v4
Create Date: 2024-01-02 20:00:00.000000

"""
from alembic import op
import sqlalchemy as sa

revision = 'fix_users_table_v4'
down_revision = None
branch_labels = None
depends_on = None

def upgrade():
    # Crear tabla temporal con la estructura correcta
    op.execute("""
    CREATE TABLE users_new (
        id SERIAL PRIMARY KEY,
        username VARCHAR(80) UNIQUE NOT NULL,
        email VARCHAR(120) UNIQUE NOT NULL,
        password_hash VARCHAR(256),
        is_active BOOLEAN DEFAULT TRUE,
        reset_code VARCHAR(6),
        reset_code_expires TIMESTAMP,
        google_id VARCHAR(100)
    )
    """)
    
    # Respaldar datos existentes
    op.execute("""
    INSERT INTO users_new (id, username, email, password_hash, is_active)
    SELECT id, username, email, password_hash, is_active 
    FROM users
    ON CONFLICT DO NOTHING
    """)
    
    # Eliminar tabla anterior y renombrar la nueva
    op.execute("DROP TABLE IF EXISTS users CASCADE")
    op.execute("ALTER TABLE users_new RENAME TO users")
    
    # Crear índices necesarios
    op.execute("CREATE INDEX ix_users_email ON users(email)")
    op.execute("CREATE INDEX ix_users_username ON users(username)")

def downgrade():
    op.execute("""
    CREATE TABLE users (
        id SERIAL PRIMARY KEY,
        username VARCHAR(80) UNIQUE NOT NULL,
        email VARCHAR(120) UNIQUE NOT NULL,
        password_hash VARCHAR(256),
        is_active BOOLEAN DEFAULT TRUE
    )
    """)
