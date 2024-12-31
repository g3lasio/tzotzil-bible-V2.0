
"""Fix last_login field

Revision ID: fix_last_login_field
Revises: b95578ef4b5c
Create Date: 2024-12-31 16:30:00.000000
"""
from alembic import op
import sqlalchemy as sa
from datetime import datetime

revision = 'fix_last_login_field'
down_revision = 'b95578ef4b5c'
branch_labels = None
depends_on = None

def upgrade():
    # Añadir la columna last_login con un valor por defecto
    op.add_column('users', sa.Column('last_login', sa.DateTime(), nullable=True, server_default=sa.text('CURRENT_TIMESTAMP')))

def downgrade():
    op.drop_column('users', 'last_login')
