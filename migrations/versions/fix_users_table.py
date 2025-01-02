
"""fix users table

Revision ID: fix_users_table
Create Date: 2024-01-02 17:55:00.000000

"""
from alembic import op
import sqlalchemy as sa

revision = 'fix_users_table'
down_revision = None
branch_labels = None
depends_on = None

def upgrade():
    # Recrear tabla users con estructura correcta
    op.execute("""
    DROP TABLE IF EXISTS users CASCADE;
    CREATE TABLE users (
        id SERIAL PRIMARY KEY,
        username VARCHAR(80) UNIQUE NOT NULL,
        email VARCHAR(120) UNIQUE NOT NULL,
        password_hash VARCHAR(256),
        is_active BOOLEAN DEFAULT TRUE,
        reset_code VARCHAR(6),
        reset_code_expires TIMESTAMP
    )
    """)

def downgrade():
    op.drop_table('users')
