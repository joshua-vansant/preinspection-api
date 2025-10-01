"""added relationships to organization

Revision ID: 60d3eb4a0d67
Revises: 9b0ae4f5eb25
Create Date: 2025-10-01 09:08:40.083521

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '60d3eb4a0d67'
down_revision = '9b0ae4f5eb25'
branch_labels = None
depends_on = None


def upgrade():
    # Add foreign key constraint for Vehicle.org_id
    op.create_foreign_key(
        'fk_vehicles_org_id',
        'vehicles', 'organizations',
        local_cols=['org_id'], remote_cols=['id'],
        source_schema='inspection_app', referent_schema='inspection_app',
        ondelete='SET NULL'
    )

    # Add foreign key constraint for Template.org_id
    op.create_foreign_key(
        'fk_templates_org_id',
        'templates', 'organizations',
        local_cols=['org_id'], remote_cols=['id'],
        source_schema='inspection_app', referent_schema='inspection_app',
        ondelete='SET NULL'
    )


def downgrade():
    op.drop_constraint('fk_vehicles_org_id', 'vehicles', schema='inspection_app', type_='foreignkey')
    op.drop_constraint('fk_templates_org_id', 'templates', schema='inspection_app', type_='foreignkey')