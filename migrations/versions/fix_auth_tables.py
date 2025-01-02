
"""fix auth tables

Revision ID: fix_auth_tables
Revises: None
Create Date: 2024-01-02 20:00:00.000000

"""
from alembic import op
import sqlalchemy as sa

def upgrade():
    # Agregar columnas faltantes a la tabla users
    op.add_column('users', sa.Column('last_login', sa.DateTime(), nullable=True))
    op.add_column('users', sa.Column('reset_code', sa.String(32), nullable=True))
    op.add_column('users', sa.Column('reset_code_expires', sa.DateTime(), nullable=True))
    
    # Crear índices
    op.create_index('idx_users_reset_code', 'users', ['reset_code'], unique=True)
    op.create_index('idx_users_email', 'users', ['email'], unique=True)

def downgrade():
    op.drop_index('idx_users_reset_code')
    op.drop_index('idx_users_email')
    op.drop_column('users', 'reset_code_expires')
    op.drop_column('users', 'reset_code')
    op.drop_column('users', 'last_login')
