"""Add user authentication and profile fields

Revision ID: 8af10b95505c
Revises: 
Create Date: 2024-11-08 17:43:14.531487

"""
from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision = '8af10b95505c'
down_revision = None
branch_labels = None
depends_on = None

def upgrade():
    # Create users table if it doesn't exist
    op.create_table('users',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('username', sa.String(length=80), nullable=False),
        sa.Column('email', sa.String(length=120), nullable=False),
        sa.Column('password_hash', sa.String(length=128), nullable=False),
        sa.Column('first_name', sa.String(length=50), nullable=True),
        sa.Column('last_name', sa.String(length=50), nullable=True),
        sa.Column('phone', sa.String(length=20), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('is_active', sa.Boolean(), nullable=False, server_default='1'),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('email'),
        sa.UniqueConstraint('username')
    )

def downgrade():
    op.drop_table('users')