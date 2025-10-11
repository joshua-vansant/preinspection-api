"""added column for inspection item to inspection_photos

Revision ID: df556125707a
Revises: 7ed5c76cf43e
Create Date: 2025-10-11 13:09:23.783054

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'df556125707a'
down_revision = '7ed5c76cf43e'
branch_labels = None
depends_on = None


def upgrade():
    # Add inspection_item_id column to inspection_photos
    op.add_column(
        'inspection_photos',
        sa.Column('inspection_item_id', sa.Integer(), nullable=True),
        schema='inspection_app'
    )

    # Create foreign key constraint to template_items
    op.create_foreign_key(
        'fk_inspection_photos_template_item_id',
        'inspection_photos',
        'template_items',
        ['inspection_item_id'],
        ['id'],
        source_schema='inspection_app',
        referent_schema='inspection_app',
        ondelete='CASCADE'
    )


def downgrade():
    # Drop the foreign key and column
    op.drop_constraint(
        'fk_inspection_photos_template_item_id',
        'inspection_photos',
        type_='foreignkey',
        schema='inspection_app'
    )
    op.drop_column('inspection_photos', 'inspection_item_id', schema='inspection_app')
