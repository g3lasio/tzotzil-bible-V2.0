
"""add reset fields

Revision ID: add_reset_fields
"""
from alembic import op
import sqlalchemy as sa

def upgrade():
    # Agregar las columnas necesarias
    with op.batch_alter_table('users', schema=None) as batch_op:
        batch_op.add_column(sa.Column('is_active', sa.Boolean(), nullable=True, server_default='true'))
        batch_op.add_column(sa.Column('reset_code', sa.String(6), nullable=True))
        batch_op.add_column(sa.Column('reset_code_expires', sa.DateTime(), nullable=True))

def downgrade():
    with op.batch_alter_table('users', schema=None) as batch_op:
        batch_op.drop_column('reset_code_expires')
        batch_op.drop_column('reset_code')
        batch_op.drop_column('is_active')
