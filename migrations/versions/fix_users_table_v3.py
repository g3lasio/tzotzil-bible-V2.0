
"""fix users table v3

Revision ID: fix_users_table_v3
Create Date: 2024-01-02 19:30:00.000000

"""
from alembic import op
import sqlalchemy as sa

revision = 'fix_users_table_v3'
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
    
    # Copiar datos existentes si la tabla existe
    op.execute("""
    INSERT INTO users_new (id, username, email, password_hash, is_active)
    SELECT id, username, email, password_hash, is_active 
    FROM users
    ON CONFLICT DO NOTHING
    """)
    
    # Eliminar tabla vieja y renombrar la nueva
    op.execute("DROP TABLE IF EXISTS users CASCADE")
    op.execute("ALTER TABLE users_new RENAME TO users")
    
    # Crear índices
    op.execute("CREATE INDEX ix_users_email ON users(email)")
    op.execute("CREATE INDEX ix_users_username ON users(username)")

def downgrade():
    op.drop_table('users')
