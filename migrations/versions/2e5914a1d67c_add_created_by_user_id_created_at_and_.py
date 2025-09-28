"""Add created_by_user_id, created_at and updated_at to Vehicle

Revision ID: 2e5914a1d67c
Revises: 9ca737586e18
Create Date: 2025-09-28 14:43:43.186215

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '2e5914a1d67c'
down_revision = '9ca737586e18'
branch_labels = None
depends_on = None


def upgrade():
    # Add created_by_user_id column
    op.add_column('vehicles', sa.Column('created_by_user_id', sa.Integer(), nullable=True), schema='inspection_app')
    op.create_foreign_key(
        'fk_vehicle_created_by_user', 'vehicles', 'user', ['created_by_user_id'], ['id'], source_schema='inspection_app', referent_schema='inspection_app'
    )

    # If you also want to ensure created_at and updated_at exist
    op.add_column('vehicles', sa.Column('created_at', sa.DateTime(), nullable=True), schema='inspection_app')
    op.add_column('vehicles', sa.Column('updated_at', sa.DateTime(), nullable=True), schema='inspection_app')


def downgrade():
    op.drop_constraint('fk_vehicle_created_by_user', 'vehicles', type_='foreignkey', schema='inspection_app')
    op.drop_column('vehicles', 'created_by_user_id', schema='inspection_app')
    op.drop_column('vehicles', 'created_at', schema='inspection_app')
    op.drop_column('vehicles', 'updated_at', schema='inspection_app')

