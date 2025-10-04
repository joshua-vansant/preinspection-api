"""edited inspection_results.vehicle_id

Revision ID: 24e962834748
Revises: 59bc7b56dd6d
Create Date: 2025-10-03 21:08:28.990224

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '24e962834748'
down_revision = '59bc7b56dd6d'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Drop existing FK constraint
    op.drop_constraint(
        'fk_vehicle', 
        'inspection_results', 
        schema='inspection_app', 
        type_='foreignkey'
    )
    
    # Alter vehicle_id to be nullable
    op.alter_column(
        'inspection_results',
        'vehicle_id',
        existing_type=sa.Integer(),
        nullable=True,
        schema='inspection_app'
    )
    
    # Recreate FK with ON DELETE SET NULL
    op.create_foreign_key(
        'fk_vehicle',
        'inspection_results',
        'vehicles',
        ['vehicle_id'],
        ['id'],
        ondelete='SET NULL',
        source_schema='inspection_app',
        referent_schema='inspection_app'
    )


def downgrade() -> None:
    # Drop modified FK
    op.drop_constraint(
        'fk_vehicle',
        'inspection_results',
        schema='inspection_app',
        type_='foreignkey'
    )
    
    # Revert vehicle_id to NOT NULL
    op.alter_column(
        'inspection_results',
        'vehicle_id',
        existing_type=sa.Integer(),
        nullable=False,
        schema='inspection_app'
    )
    
    # Recreate original FK without ON DELETE SET NULL
    op.create_foreign_key(
        'fk_vehicle',
        'inspection_results',
        'vehicles',
        ['vehicle_id'],
        ['id'],
        source_schema='inspection_app',
        referent_schema='inspection_app'
    )