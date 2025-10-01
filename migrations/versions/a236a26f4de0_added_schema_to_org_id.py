"""added schema to org_id

Revision ID: a236a26f4de0
Revises: c64c09df5a07
Create Date: 2025-10-01 13:04:20.106999

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'a236a26f4de0'
down_revision = 'c64c09df5a07'
branch_labels = None
depends_on = None


def upgrade():
    # Drop the old foreign key first
    op.drop_constraint(
        'fk_inspection_results_org_id',  # name of old FK, adjust if different
        'inspection_results',
        schema='inspection_app',
        type_='foreignkey'
    )

    # Create the new schema-qualified foreign key
    op.create_foreign_key(
        'fk_inspection_results_org_id',
        'inspection_results', 'organizations',
        local_cols=['org_id'], remote_cols=['id'],
        source_schema='inspection_app',
        referent_schema='inspection_app',
        ondelete='SET NULL'
    )


def downgrade():
    # Drop the new schema-qualified FK
    op.drop_constraint(
        'fk_inspection_results_org_id',
        'inspection_results',
        schema='inspection_app',
        type_='foreignkey'
    )

    # Recreate the old foreign key (without schema qualification)
    op.create_foreign_key(
        'fk_inspection_results_org_id',
        'inspection_results', 'organizations',
        local_cols=['org_id'], remote_cols=['id'],
        ondelete='SET NULL'
    )
