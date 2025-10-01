"""made inspection_results.driver_id nullable

Revision ID: 59bc7b56dd6d
Revises: a236a26f4de0
Create Date: 2025-10-01 13:12:47.352151

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '59bc7b56dd6d'
down_revision = 'a236a26f4de0'
branch_labels = None
depends_on = None


def upgrade():
    op.alter_column(
        'inspection_results',
        'driver_id',
        existing_type=sa.Integer(),
        nullable=True,
        schema='inspection_app'
    )


def downgrade():
    op.alter_column(
        'inspection_results',
        'driver_id',
        existing_type=sa.Integer(),
        nullable=False,
        schema='inspection_app'
    )
