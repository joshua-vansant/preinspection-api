"""added driver name columns to inspection_results

Revision ID: d2084dfbca6b
Revises: bc7665a65473
Create Date: 2025-10-14 09:57:07.018757

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'd2084dfbca6b'
down_revision = 'bc7665a65473'
branch_labels = None
depends_on = None


def upgrade():
    # Add columns to store driver snapshot
    op.add_column(
        'inspection_results',
        sa.Column('driver_first_name', sa.String(length=50), nullable=True),
        schema='inspection_app'
    )
    op.add_column(
        'inspection_results',
        sa.Column('driver_last_name', sa.String(length=50), nullable=True),
        schema='inspection_app'
    )
    op.add_column(
        'inspection_results',
        sa.Column('driver_full_name', sa.String(length=100), nullable=True),
        schema='inspection_app'
    )

def downgrade():
    # Remove the columns in reverse
    op.drop_column('inspection_results', 'driver_full_name', schema='inspection_app')
    op.drop_column('inspection_results', 'driver_last_name', schema='inspection_app')
    op.drop_column('inspection_results', 'driver_first_name', schema='inspection_app')