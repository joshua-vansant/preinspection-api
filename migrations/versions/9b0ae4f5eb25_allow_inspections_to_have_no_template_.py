"""allow inspections to have no template assigned

Revision ID: 9b0ae4f5eb25
Revises: 5469e991adbb
Create Date: 2025-10-01 08:57:33.383501

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '9b0ae4f5eb25'
down_revision = '5469e991adbb'
branch_labels = None
depends_on = None


def upgrade():
    op.alter_column(
        'inspection_results',          
        'template_id',                
        existing_type=sa.Integer(),
        nullable=True,
        schema='inspection_app'
    )


def downgrade():
    op.alter_column(
        'inspection_results',
        'template_id',
        existing_type=sa.Integer(),
        nullable=False,
        schema='inspection_app'
    )