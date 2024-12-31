
"""Remove favorites table

Revision ID: remove_favorites
Revises: 8af10b95505c
Create Date: 2024-12-31 03:15:00.000000

"""
from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision = 'remove_favorites'
down_revision = '8af10b95505c'
branch_labels = None
depends_on = None

def upgrade():
    op.drop_table('favorite')

def downgrade():
    op.create_table('favorite',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('verse_id', sa.Integer(), nullable=False),
        sa.Column('user_id', sa.Integer(), nullable=False),
        sa.Column('created_at', sa.DateTime(), nullable=True),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ),
        sa.ForeignKeyConstraint(['verse_id'], ['bibleverse.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
