
"""fix user sequence

Revision ID: fix_user_sequence
Create Date: 2024-01-04 17:00:00.000000
"""
from alembic import op

def upgrade():
    # Reiniciar la secuencia basándose en el máximo ID existente
    op.execute("""
    SELECT setval('user_id_seq', (SELECT MAX(id) FROM users));
    ALTER TABLE users ALTER COLUMN id SET DEFAULT nextval('user_id_seq');
    """)

def downgrade():
    pass
