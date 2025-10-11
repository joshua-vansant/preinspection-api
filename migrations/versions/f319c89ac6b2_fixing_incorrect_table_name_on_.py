"""fixing incorrect table name on inspection_item_id

Revision ID: f319c89ac6b2
Revises: df556125707a
Create Date: 2025-10-11 13:16:04.713818

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'f319c89ac6b2'
down_revision = 'df556125707a'
branch_labels = None
depends_on = None


def upgrade():
    conn = op.get_bind()

    # Check if the constraint exists before trying to drop it
    constraint_check = conn.execute(sa.text("""
        SELECT constraint_name
        FROM information_schema.table_constraints
        WHERE table_schema = 'inspection_app'
          AND table_name = 'inspection_photos'
          AND constraint_type = 'FOREIGN KEY'
          AND constraint_name = 'inspection_photos_inspection_item_id_fkey';
    """)).fetchone()

    if constraint_check:
        op.drop_constraint(
            'inspection_photos_inspection_item_id_fkey',
            'inspection_photos',
            schema='inspection_app',
            type_='foreignkey'
        )

    # Now safely create the correct FK to template_items
    op.create_foreign_key(
        'inspection_photos_inspection_item_id_fkey',
        'inspection_photos',
        'template_items',
        ['inspection_item_id'],
        ['id'],
        source_schema='inspection_app',
        referent_schema='inspection_app',
        ondelete='CASCADE'
    )

def downgrade():
    conn = op.get_bind()

    # Drop the corrected foreign key if it exists
    constraint_check = conn.execute(sa.text("""
        SELECT constraint_name
        FROM information_schema.table_constraints
        WHERE table_schema = 'inspection_app'
          AND table_name = 'inspection_photos'
          AND constraint_type = 'FOREIGN KEY'
          AND constraint_name = 'inspection_photos_inspection_item_id_fkey';
    """)).fetchone()

    if constraint_check:
        op.drop_constraint(
            'inspection_photos_inspection_item_id_fkey',
            'inspection_photos',
            schema='inspection_app',
            type_='foreignkey'
        )

    # Recreate the original FK to inspection_items (for rollback)
    op.create_foreign_key(
        'inspection_photos_inspection_item_id_fkey',
        'inspection_photos',
        'inspection_items',
        ['inspection_item_id'],
        ['id'],
        source_schema='inspection_app',
        referent_schema='inspection_app',
        ondelete='CASCADE'
    )

