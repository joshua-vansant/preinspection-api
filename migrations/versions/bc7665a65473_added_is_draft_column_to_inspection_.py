"""added is_draft column to inspection_results

Revision ID: bc7665a65473
Revises: f319c89ac6b2
Create Date: 2025-10-11 22:17:42.521458

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'bc7665a65473'
down_revision = 'f319c89ac6b2'
branch_labels = None
depends_on = None


def upgrade():
    op.add_column(
        'inspection_results',
        sa.Column('is_draft', sa.Boolean(), nullable=False, server_default=sa.sql.expression.true()),
        schema='inspection_app'
    )
    op.alter_column(
        'inspection_results',
        'is_draft',
        server_default=None,
        schema='inspection_app'
    )


def downgrade():
    op.drop_column(
        'inspection_results',
        'is_draft',
        schema='inspection_app'
    )