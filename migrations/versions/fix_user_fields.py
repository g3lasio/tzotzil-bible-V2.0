
"""fix user fields

Revision ID: fix_user_fields
Revises: add_subscription_fields
Create Date: 2024-01-04 12:00:00.000000
"""
from alembic import op
import sqlalchemy as sa

revision = 'fix_user_fields'
down_revision = 'add_subscription_fields'
branch_labels = None
depends_on = None

def upgrade():
    # Agregar campos faltantes para el signup
    op.add_column('users', sa.Column('lastname', sa.String(50), nullable=True))
    op.add_column('users', sa.Column('phone', sa.String(15), nullable=True))
    
    # Actualizar columnas a not nullable después de migrar datos existentes
    op.execute("UPDATE users SET lastname = '' WHERE lastname IS NULL")
    op.execute("UPDATE users SET phone = '' WHERE phone IS NULL")
    
    op.alter_column('users', 'lastname',
                    existing_type=sa.String(50),
                    nullable=False)
    op.alter_column('users', 'phone',
                    existing_type=sa.String(15),
                    nullable=False)

def downgrade():
    op.drop_column('users', 'lastname')
    op.drop_column('users', 'phone')
