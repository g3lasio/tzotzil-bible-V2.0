
"""add reset fields

Revision ID: add_reset_fields
"""
from alembic import op
import sqlalchemy as sa

def upgrade():
    # Drop existing table and recreate with all fields
    op.drop_table('users')
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

def downgrade():
    op.drop_table('users')
