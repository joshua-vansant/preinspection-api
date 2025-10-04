"""inspection_results.driver_id will set nulls on delete

Revision ID: 9172f94b6c7d
Revises: 914d0d6df6bb
Create Date: 2025-10-03 22:48:36.554032

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '9172f94b6c7d'
down_revision = '914d0d6df6bb'
branch_labels = None
depends_on = None

def upgrade():
    op.drop_constraint(
        'inspection_results_driver_id_fkey',
        'inspection_results',
        type_='foreignkey',
        schema='inspection_app'
    )
    op.create_foreign_key(
        'inspection_results_driver_id_fkey',  # constraint name
        'inspection_results',                  # source table
        'user',                                # referent table
        local_cols=['driver_id'],
        remote_cols=['id'],
        ondelete='SET NULL',
        source_schema='inspection_app',
        referent_schema='inspection_app'
    )

def downgrade():
    op.drop_constraint(
        'inspection_results_driver_id_fkey',
        'inspection_results',
        type_='foreignkey',
        schema='inspection_app'
    )
    op.create_foreign_key(
        'inspection_results_driver_id_fkey',
        'inspection_results',
        'user',
        local_cols=['driver_id'],
        remote_cols=['id'],
        source_schema='inspection_app',
        referent_schema='inspection_app'
    )
