"""added additional columns and helper methods to inspection_results

Revision ID: 181d9256c516
Revises: 2e5914a1d67c
Create Date: 2025-09-29 09:58:44.148321

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '181d9256c516'
down_revision = '2e5914a1d67c'
branch_labels = None
depends_on = None


def upgrade():
    # Add new columns to inspection_results table
    op.add_column('inspection_results', sa.Column('start_mileage', sa.Integer(), nullable=True), schema='inspection_app')
    op.add_column('inspection_results', sa.Column('end_mileage', sa.Integer(), nullable=True), schema='inspection_app')
    op.add_column('inspection_results', sa.Column('odometer_verified', sa.Boolean(), nullable=True, server_default=sa.sql.expression.false()), schema='inspection_app')
    op.add_column('inspection_results', sa.Column('fuel_level', sa.Float(), nullable=True), schema='inspection_app')
    op.add_column('inspection_results', sa.Column('fuel_notes', sa.Text(), nullable=True), schema='inspection_app')


def downgrade():
    # Remove the columns if rolling back
    op.drop_column('inspection_results', 'fuel_notes', schema='inspection_app',)
    op.drop_column('inspection_results', 'fuel_level', schema='inspection_app')
    op.drop_column('inspection_results', 'odometer_verified', schema='inspection_app')
    op.drop_column('inspection_results', 'end_mileage', schema='inspection_app')
    op.drop_column('inspection_results', 'start_mileage', schema='inspection_app')
