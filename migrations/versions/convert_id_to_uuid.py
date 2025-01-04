
"""convert id to uuid

Revision ID: convert_id_to_uuid
Create Date: 2024-01-04 20:00:00.000000
"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects.postgresql import UUID
import uuid

def upgrade():
    # Convertir la columna id a UUID
    op.alter_column('users', 'id',
        type_=UUID(as_uuid=True),
        postgresql_using="id::uuid",
        existing_nullable=False)

def downgrade():
    op.alter_column('users', 'id',
        type_=sa.String(36),
        postgresql_using="id::varchar")
