"""add password_reset_tokens table

Revision ID: ef455f9bf05e
Revises: d2084dfbca6b
Create Date: 2025-11-07 13:07:23.455668
"""
from alembic import op
import sqlalchemy as sa
from datetime import datetime

# revision identifiers, used by Alembic.
revision = 'ef455f9bf05e'
down_revision = 'd2084dfbca6b'
branch_labels = None
depends_on = None

schema_name = 'inspection_app'


def upgrade():
    op.create_table(
        'password_reset_tokens',
        sa.Column('id', sa.Integer(), primary_key=True),
        sa.Column('user_id', sa.Integer(), sa.ForeignKey(f'{schema_name}.user.id', ondelete='CASCADE'), nullable=False),
        sa.Column('token', sa.String(length=128), nullable=False, unique=True, index=True),
        sa.Column('expires_at', sa.DateTime(), nullable=False),
        sa.Column('created_at', sa.DateTime(), nullable=False, default=datetime.utcnow),
        schema=schema_name
    )

    op.create_index(
        'ix_password_reset_tokens_token',
        'password_reset_tokens', 
        ['token'],
        unique=True,
        schema=schema_name
    )


def downgrade():
    op.drop_index(
        'ix_password_reset_tokens_token',
        table_name='password_reset_tokens',
        schema=schema_name
    )
    op.drop_table('password_reset_tokens', schema=schema_name)
