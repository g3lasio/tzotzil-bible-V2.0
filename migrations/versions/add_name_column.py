
"""add_name_column

Revision ID: add_name_column
Create Date: 2024-01-04 18:00:00.000000
"""
from alembic import op
import sqlalchemy as sa

def upgrade():
    op.add_column('users', sa.Column('name', sa.String(50), nullable=True))

def downgrade():
    op.drop_column('users', 'name')
