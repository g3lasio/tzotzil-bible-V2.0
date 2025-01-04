
"""Add user profile fields

Revision ID: add_user_profile_fields
Revises: add_nevin_fields
Create Date: 2024-01-04 17:55:00.000000

"""
from alembic import op
import sqlalchemy as sa

# revision identifiers
revision = 'add_user_profile_fields'
down_revision = 'add_nevin_fields'
branch_labels = None
depends_on = None

def upgrade():
    op.add_column('users',
        sa.Column('first_name', sa.String(50), nullable=True)
    )

def downgrade():
    op.drop_column('users', 'first_name')
