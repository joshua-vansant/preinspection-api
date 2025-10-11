"""removed inspection_results.photo_url and created inspection_photos table

Revision ID: 7ed5c76cf43e
Revises: 9a921f4a87cc
Create Date: 2025-10-10 22:11:50.272249

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '7ed5c76cf43e'
down_revision = '9a921f4a87cc'
branch_labels = None
depends_on = None


def upgrade():
    # Create inspection_photos table in schema inspection_app
    op.create_table(
        'inspection_photos',
        sa.Column('id', sa.Integer, primary_key=True),
        sa.Column('inspection_id', sa.Integer, sa.ForeignKey('inspection_app.inspection_results.id', ondelete='CASCADE'), nullable=False),
        sa.Column('driver_id', sa.Integer, sa.ForeignKey('inspection_app.user.id', ondelete='SET NULL'), nullable=True),
        sa.Column('photo_url', sa.String(length=255), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now()),
        schema='inspection_app'
    )

    # Drop photo_url from inspection_results
    op.drop_column('inspection_results', 'photo_url', schema='inspection_app')


def downgrade():
    # Add photo_url back to inspection_results
    op.add_column('inspection_results', sa.Column('photo_url', sa.String(length=255), nullable=True), schema='inspection_app')

    # Drop inspection_photos table
    op.drop_table('inspection_photos', schema='inspection_app')
