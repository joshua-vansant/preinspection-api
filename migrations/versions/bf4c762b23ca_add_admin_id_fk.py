"""add admin_id fk

Revision ID: bf4c762b23ca
Revises: 353ee0154886
Create Date: 2025-09-22 20:53:03.204521

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'bf4c762b23ca'
down_revision = '353ee0154886'
branch_labels = None
depends_on = None


def upgrade():
    op.create_foreign_key(
        "fk_organizations_admin_id_user",
        "organizations", "user",
        ["admin_id"], ["id"],
        source_schema="inspection_app",
        referent_schema="inspection_app"
    )

def downgrade():
    op.drop_constraint(
        "fk_organizations_admin_id_user",
        "organizations",
        schema="inspection_app"
    )

