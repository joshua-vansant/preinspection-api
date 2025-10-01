"""added org_id to inspection results

Revision ID: c64c09df5a07
Revises: 60d3eb4a0d67
Create Date: 2025-10-01 12:50:26.834790

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'c64c09df5a07'
down_revision = '60d3eb4a0d67'
branch_labels = None
depends_on = None


def upgrade():
    # Add org_id column to inspection_results
    op.add_column(
        'inspection_results',
        sa.Column('org_id', sa.Integer(), nullable=True),
        schema='inspection_app'
    )

    # Add foreign key constraint to organizations.id
    op.create_foreign_key(
        'fk_inspection_results_org_id',
        'inspection_results',
        'organizations',
        local_cols=['org_id'],
        remote_cols=['id'],
        source_schema='inspection_app',
        referent_schema='inspection_app',
        ondelete='SET NULL'
    )

    # Backfill org_id for existing rows based on their driver’s org
    op.execute("""
        UPDATE inspection_app.inspection_results ir
        SET org_id = u.org_id
        FROM inspection_app.user u
        WHERE ir.driver_id = u.id
    """)


def downgrade():
    # Drop foreign key and column
    op.drop_constraint(
        'fk_inspection_results_org_id',
        'inspection_results',
        schema='inspection_app',
        type_='foreignkey'
    )
    op.drop_column('inspection_results', 'org_id', schema='inspection_app')
