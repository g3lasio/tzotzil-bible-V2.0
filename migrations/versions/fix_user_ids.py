
"""fix user ids and sequence

Revision ID: fix_user_ids
Create Date: 2024-01-04 17:30:00.000000
"""
from alembic import op
import sqlalchemy as sa

def upgrade():
    # Crear nueva secuencia
    op.execute("""
    DO $$
    BEGIN
        DROP SEQUENCE IF EXISTS users_id_seq CASCADE;
        CREATE SEQUENCE users_id_seq;
        SELECT setval('users_id_seq', COALESCE((SELECT MAX(id) FROM users), 0) + 1);
        ALTER TABLE users ALTER COLUMN id SET DEFAULT nextval('users_id_seq');
        ALTER SEQUENCE users_id_seq OWNED BY users.id;
    END $$;
    """)

def downgrade():
    pass
