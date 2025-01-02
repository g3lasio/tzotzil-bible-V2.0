
"""add reset fields

Revision ID: add_reset_fields
"""
from alembic import op
import sqlalchemy as sa

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
        sa.Column('password_hash', sa.String(128)),
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
    op.drop_table('users')
