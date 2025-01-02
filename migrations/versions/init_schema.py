
"""init schema

Revision ID: init_schema
Create Date: 2024-01-02 21:00:00.000000
"""
from alembic import op
import sqlalchemy as sa

revision = 'init_schema'
down_revision = None
branch_labels = None
depends_on = None

def upgrade():
    op.create_table('users',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('username', sa.String(80), unique=True, nullable=False),
        sa.Column('email', sa.String(120), unique=True, nullable=False),
        sa.Column('password_hash', sa.String(256), nullable=False),
        sa.Column('is_active', sa.Boolean(), default=True),
        sa.PrimaryKeyConstraint('id')
    )
    
    op.create_index('ix_users_email', 'users', ['email'])
    op.create_index('ix_users_username', 'users', ['username'])

def downgrade():
    op.drop_table('users')
