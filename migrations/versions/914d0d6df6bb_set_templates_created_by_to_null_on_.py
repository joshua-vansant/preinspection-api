"""set templates.created_by to null on deletion. allow nulls there as well

Revision ID: 914d0d6df6bb
Revises: 24e962834748
Create Date: 2025-10-03 22:28:10.376659

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '914d0d6df6bb'
down_revision = '24e962834748'
branch_labels = None
depends_on = None


def upgrade():
    # Drop existing foreign key
    op.drop_constraint(
        "templates_created_by_fkey",
        "templates",
        schema="inspection_app",
        type_="foreignkey"
    )
    # Alter column to be nullable
    op.alter_column(
        "templates",
        "created_by",
        existing_type=sa.Integer(),
        nullable=True,
        schema="inspection_app"
    )
    # Re-create foreign key with ON DELETE SET NULL
    op.create_foreign_key(
        "templates_created_by_fkey",
        "templates",
        "user",
        ["created_by"],
        ["id"],
        source_schema="inspection_app",
        referent_schema="inspection_app",
        ondelete="SET NULL"
    )


def downgrade():
    # Drop the modified foreign key
    op.drop_constraint(
        "templates_created_by_fkey",
        "templates",
        schema="inspection_app",
        type_="foreignkey"
    )
    # Alter column to be non-nullable
    op.alter_column(
        "templates",
        "created_by",
        existing_type=sa.Integer(),
        nullable=False,
        schema="inspection_app"
    )
    # Re-create original foreign key without ON DELETE SET NULL
    op.create_foreign_key(
        "templates_created_by_fkey",
        "templates",
        "user",
        ["created_by"],
        ["id"],
        source_schema="inspection_app",
        referent_schema="inspection_app"
    )