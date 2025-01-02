
"""recreate users table

Revision ID: recreate_users_table
Revises: add_reset_fields
Create Date: 2024-01-02 17:43:14.531487

"""
from alembic import op
import sqlalchemy as sa

# revision identifiers
revision = 'recreate_users_table'
down_revision = 'add_reset_fields'
branch_labels = None
depends_on = None

def upgrade():
    # Eliminar tabla si existe
    op.drop_table('users', if_exists=True)
    
    # Crear nueva tabla users con todos los campos necesarios
    op.create_table('users',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('username', sa.String(80), unique=True, nullable=False),
        sa.Column('email', sa.String(120), unique=True, nullable=False),
        sa.Column('password_hash', sa.String(256)),
        sa.Column('is_active', sa.Boolean(), default=True),
        sa.Column('reset_code', sa.String(6), nullable=True),
        sa.Column('reset_code_expires', sa.DateTime(), nullable=True),
        sa.PrimaryKeyConstraint('id')
    )

def downgrade():
    op.drop_table('users')
