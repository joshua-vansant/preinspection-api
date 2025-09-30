"""added admin_invite_code to org table

Revision ID: 5469e991adbb
Revises: b2ba7a78bf48
Create Date: 2025-09-30 14:42:22.930587

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '5469e991adbb'
down_revision = 'b2ba7a78bf48'
branch_labels = None
depends_on = None


def upgrade():
    op.add_column(
        'organizations',
        sa.Column('admin_invite_code', sa.String(length=32), nullable=True),
        schema='inspection_app'
    )


def downgrade():
    op.drop_column(
        'organizations',
        'admin_invite_code',
        schema='inspection_app'
    )