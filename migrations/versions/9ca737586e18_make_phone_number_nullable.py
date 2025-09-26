"""make phone_number nullable

Revision ID: 9ca737586e18
Revises: fc3e42b8b4f5
Create Date: 2025-09-26 11:04:38.028555

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '9ca737586e18'
down_revision = 'fc3e42b8b4f5'
branch_labels = None
depends_on = None


def upgrade():
    op.alter_column(
        'user',
        'phone_number',
        existing_type=sa.String(length=15),
        nullable=True,
        schema='inspection_app'
    )

def downgrade():
    op.alter_column(
        'user',
        'phone_number',
        existing_type=sa.String(length=15),
        nullable=False,
        schema='inspection_app'
    )