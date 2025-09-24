"""changed created_at to use timezone

Revision ID: e12af2b57b54
Revises: c486d19c2c79
Create Date: 2025-09-24 13:18:03.544227

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'e12af2b57b54'
down_revision = 'c486d19c2c79'
branch_labels = None
depends_on = None


def upgrade():
    op.alter_column(
        'inspection_results',
        'created_at',
        existing_type=sa.DateTime(),
        server_default=None,
        existing_nullable=False,
        schema='inspection_app'
    )

def downgrade():
    op.alter_column(
        'inspection_results',
        'created_at',
        existing_type=sa.DateTime(),
        server_default=sa.text('CURRENT_TIMESTAMP'),
        existing_nullable=False,
        schema='inspection_app'
    )