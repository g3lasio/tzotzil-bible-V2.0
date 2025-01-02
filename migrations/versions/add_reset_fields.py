"""add reset fields

Revision ID: add_reset_fields
Revises: 8af10b95505c
Create Date: 2024-01-02 16:55:00.000000

"""
from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision = 'add_reset_fields'
down_revision = '8af10b95505c'
branch_labels = None
depends_on = None

def upgrade():
    # Primero hacemos backup de los usuarios existentes
    op.execute('CREATE TABLE users_backup AS SELECT id, username, email, password_hash FROM users')

    # Eliminamos la tabla actual
    op.drop_table('users')

    # Creamos la tabla con todos los campos necesarios
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

    # Restauramos los datos
    op.execute('INSERT INTO users (id, username, email, password_hash) SELECT id, username, email, password_hash FROM users_backup')

    # Eliminamos la tabla de backup
    op.execute('DROP TABLE users_backup')

def downgrade():
    op.drop_column('users', 'reset_code_expires')
    op.drop_column('users', 'reset_code')
"""Add reset fields

Revision ID: add_reset_fields
Revises: fix_last_login_field
Create Date: 2025-01-02 17:30:00.000000
"""
from alembic import op
import sqlalchemy as sa

# revision identifiers
revision = 'add_reset_fields'
down_revision = 'fix_last_login_field'
branch_labels = None
depends_on = None

def upgrade():
    op.add_column('users', sa.Column('reset_code', sa.String(6), nullable=True))
    op.add_column('users', sa.Column('reset_code_expires', sa.DateTime(), nullable=True))

def downgrade():
    op.drop_column('users', 'reset_code')
    op.drop_column('users', 'reset_code_expires')
