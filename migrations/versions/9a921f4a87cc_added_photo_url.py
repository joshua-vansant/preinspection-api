"""added photo_url

Revision ID: 9a921f4a87cc
Revises: 9172f94b6c7d
Create Date: 2025-10-10 20:09:03.989599

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '9a921f4a87cc'
down_revision = '9172f94b6c7d'
branch_labels = None
depends_on = None


def upgrade():
    # Add the photo_url column to inspection_results
    op.add_column(
        'inspection_results',
        sa.Column('photo_url', sa.String(length=255), nullable=True),
        schema='inspection_app'
    )

def downgrade():
    # Remove the photo_url column
    op.drop_column('inspection_results', 'photo_url', schema='inspection_app')

