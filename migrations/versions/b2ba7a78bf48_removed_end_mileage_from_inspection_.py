"""removed end_mileage from inspection_results

Revision ID: b2ba7a78bf48
Revises: 5ba8b75100ac
Create Date: 2025-09-29 18:37:36.933806

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'b2ba7a78bf48'
down_revision = '5ba8b75100ac'
branch_labels = None
depends_on = None


def upgrade():
    with op.batch_alter_table('inspection_results', schema='inspection_app') as batch_op:
        batch_op.drop_column('end_mileage')


def downgrade():
    with op.batch_alter_table('inspection_results', schema='inspection_app') as batch_op:
        batch_op.add_column(sa.Column('end_mileage', sa.Integer(), nullable=True))
