"""jwt auth update

Revision ID: jwt_auth_update
Revises: recreate_users_table
Create Date: 2025-01-02 10:00:00.000000

"""
from alembic import op
import sqlalchemy as sa

# revision identifiers
revision = 'jwt_auth_update'
down_revision = 'recreate_users_table'
branch_labels = None
depends_on = None

def upgrade():
    # Modificar la tabla users para JWT
    op.execute('COMMIT')
    op.create_table('users_new',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('username', sa.String(80), unique=True, nullable=False),
        sa.Column('email', sa.String(120), unique=True, nullable=False),
        sa.Column('password_hash', sa.String(256)),
        sa.Column('is_active', sa.Boolean(), default=True),
        sa.PrimaryKeyConstraint('id')
    )
    
    # Crear índices
    op.create_index('ix_users_email', 'users_new', ['email'], unique=True)
    op.create_index('ix_users_username', 'users_new', ['username'], unique=True)
    
    # Eliminar campos antiguos no necesarios
    op.drop_table('users')
    op.rename_table('users_new', 'users')

def downgrade():
    op.drop_table('users')
