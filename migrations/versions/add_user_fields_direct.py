
"""add user fields direct

Revision ID: add_user_fields_direct
Create Date: 2024-01-04 13:00:00.000000
"""
from alembic import op
import sqlalchemy as sa

revision = 'add_user_fields_direct'
down_revision = None
branch_labels = None
depends_on = None

def upgrade():
    # SQL directo para agregar las columnas
    op.execute("""
    ALTER TABLE users 
    ADD COLUMN IF NOT EXISTS lastname VARCHAR(50) DEFAULT '',
    ADD COLUMN IF NOT EXISTS phone VARCHAR(15) DEFAULT '';
    """)

def downgrade():
    op.execute("""
    ALTER TABLE users 
    DROP COLUMN IF EXISTS lastname,
    DROP COLUMN IF EXISTS phone;
    """)
