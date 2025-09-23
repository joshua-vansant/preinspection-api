"""add type and vehicle_id to inspection_results

Revision ID: c486d19c2c53
Revises: 87885d9045bb
Create Date: 2025-09-22 21:57:40.584406

"""
from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision = 'c486d19c2c79'
down_revision = '87885d9045bb'
branch_labels = None
depends_on = None

def upgrade():
    with op.batch_alter_table('inspection_results', schema='inspection_app') as batch_op:
        batch_op.add_column(sa.Column('vehicle_id', sa.Integer(), nullable=False))
        batch_op.add_column(sa.Column('type', sa.String(length=50), nullable=False))
        batch_op.create_foreign_key(
            'fk_vehicle',
            'vehicles',
            ['vehicle_id'],
            ['id'],
            referent_schema='inspection_app'
        )


def downgrade():
    with op.batch_alter_table('inspection_results', schema='inspection_app') as batch_op:
        batch_op.drop_constraint('fk_vehicle', type_='foreignkey')
        batch_op.drop_column('vehicle_id')
        batch_op.drop_column('type')

