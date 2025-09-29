"""setting fuel level to default to 0 instead of Null

Revision ID: 5ba8b75100ac
Revises: 181d9256c516
Create Date: 2025-09-29 10:06:07.639776

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '5ba8b75100ac'
down_revision = '181d9256c516'
branch_labels = None
depends_on = None


def upgrade():
    # Set server default for fuel_level
    op.alter_column(
        'inspection_results',
        'fuel_level',
        server_default='0',
        existing_type=sa.Float(),
        schema='inspection_app'
    )

    # update existing rows
    op.execute("UPDATE inspection_app.inspection_results SET fuel_level = 0 WHERE fuel_level IS NULL")


def downgrade():
    # Remove server default
    op.alter_column(
        'inspection_results',
        'fuel_level',
        server_default=None,
        existing_type=sa.Float(),
        schema='inspection_app'
    )
