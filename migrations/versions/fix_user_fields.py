
"""Add user fields

Revision ID: fix_user_fields_v6
Revises: fix_users_table_v4
Create Date: 2024-01-04 09:00:00.000000

"""
from alembic import op
import sqlalchemy as sa

revision = 'fix_user_fields_v6'
down_revision = 'fix_users_table_v4'
branch_labels = None
depends_on = None

def upgrade():
    # Eliminar columnas existentes si las hay
    op.execute("""
    DO $$ 
    BEGIN
        ALTER TABLE users DROP COLUMN IF EXISTS lastname;
        ALTER TABLE users DROP COLUMN IF EXISTS phone;
    EXCEPTION WHEN undefined_column THEN
        NULL;
    END $$;
    """)
    
    # Agregar las columnas con valores por defecto
    op.add_column('users', sa.Column('lastname', sa.String(50), nullable=False, server_default=''))
    op.add_column('users', sa.Column('phone', sa.String(15), nullable=False, server_default=''))

def downgrade():
    op.drop_column('users', 'lastname')
    op.drop_column('users', 'phone')
