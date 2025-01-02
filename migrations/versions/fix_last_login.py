
"""Fix last_login field

Revision ID: fix_last_login_field
Revises: b95578ef4b5c
Create Date: 2024-12-31 16:30:00.000000
"""
from alembic import op
import sqlalchemy as sa

# revision identifiers
revision = 'fix_last_login_field'
down_revision = 'b95578ef4b5c'
branch_labels = None
depends_on = None

def upgrade():
    # Crear tabla temporal con estructura actualizada
    op.execute("""
    CREATE TABLE users_new (
        id SERIAL PRIMARY KEY,
        username VARCHAR(80) UNIQUE NOT NULL,
        email VARCHAR(120) UNIQUE NOT NULL,
        password_hash VARCHAR(256),
        is_active BOOLEAN DEFAULT TRUE,
        last_login TIMESTAMP,
        reset_code VARCHAR(32),
        reset_code_expires TIMESTAMP
    )
    """)
    
    # Migrar datos existentes
    op.execute("""
    INSERT INTO users_new (id, username, email, password_hash, is_active)
    SELECT id, username, email, password_hash, is_active 
    FROM users
    """)
    
    # Reemplazar tabla
    op.execute("DROP TABLE users CASCADE")
    op.execute("ALTER TABLE users_new RENAME TO users")
    
    # Recrear índices
    op.execute("CREATE INDEX ix_users_email ON users(email)")
    op.execute("CREATE INDEX ix_users_username ON users(username)")

def downgrade():
    op.execute("ALTER TABLE users DROP COLUMN last_login")
