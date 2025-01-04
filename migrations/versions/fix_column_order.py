
"""fix column order

Revision ID: fix_column_order
Create Date: 2024-01-04 16:00:00.000000
"""
from alembic import op
import sqlalchemy as sa

revision = 'fix_column_order'
down_revision = None
branch_labels = None
depends_on = None

def upgrade():
    op.execute("""
    CREATE TABLE users_temp (
        id SERIAL PRIMARY KEY,
        username VARCHAR(80) UNIQUE NOT NULL,
        lastname VARCHAR(50) NOT NULL,
        phone VARCHAR(15) NOT NULL,
        email VARCHAR(120) UNIQUE NOT NULL,
        password_hash VARCHAR(256),
        is_active BOOLEAN DEFAULT TRUE,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        nevin_access BOOLEAN DEFAULT TRUE,
        trial_ends_at TIMESTAMP,
        trial_started_at TIMESTAMP,
        plan_type VARCHAR(20) DEFAULT 'Free' NOT NULL,
        subscription_start TIMESTAMP,
        subscription_status VARCHAR(20) DEFAULT 'inactive' NOT NULL
    );

    INSERT INTO users_temp 
    SELECT id, username, lastname, phone, email, password_hash, is_active, 
           created_at, nevin_access, trial_ends_at, trial_started_at,
           plan_type, subscription_start, subscription_status
    FROM users;

    DROP TABLE users;
    ALTER TABLE users_temp RENAME TO users;
    
    CREATE INDEX ix_users_email ON users(email);
    CREATE INDEX ix_users_username ON users(username);
    """)

def downgrade():
    pass
