"""add new columns to tables

Revision ID: fc3e42b8b4f5
Revises: e12af2b57b54
Create Date: 2025-09-26 10:46:37.981884

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'fc3e42b8b4f5'
down_revision = 'e12af2b57b54'
branch_labels = None
depends_on = None


def upgrade():
    # --- user table ---
    op.add_column('user', sa.Column('first_name', sa.String(length=30), nullable=False), schema='inspection_app')
    op.add_column('user', sa.Column('last_name', sa.String(length=30), nullable=False), schema='inspection_app')
    op.add_column('user', sa.Column('phone_number', sa.String(length=15), nullable=True), schema='inspection_app')
    op.add_column('user', sa.Column('updated_at', sa.DateTime(), nullable=True), schema='inspection_app')

    # --- vehicles table ---
    op.add_column('vehicles', sa.Column('make', sa.String(length=20), nullable=True), schema='inspection_app')
    op.add_column('vehicles', sa.Column('model', sa.String(length=20), nullable=True), schema='inspection_app')
    op.add_column('vehicles', sa.Column('year', sa.Integer(), nullable=True), schema='inspection_app')
    op.add_column('vehicles', sa.Column('vin', sa.String(length=25), nullable=True), schema='inspection_app')
    op.add_column('vehicles', sa.Column('license_plate', sa.String(length=10), nullable=False), schema='inspection_app')
    op.add_column('vehicles', sa.Column('mileage', sa.Integer(), nullable=True), schema='inspection_app')
    op.add_column('vehicles', sa.Column('status', sa.String(length=20), nullable=False, server_default="active"), schema='inspection_app')

    # --- organizations table ---
    op.add_column('organizations', sa.Column('address', sa.String(length=255), nullable=True), schema='inspection_app')
    op.add_column('organizations', sa.Column('phone_number', sa.String(length=20), nullable=True), schema='inspection_app')
    op.add_column('organizations', sa.Column('contact_name', sa.String(length=100), nullable=True), schema='inspection_app')
    op.add_column('organizations', sa.Column('updated_at', sa.DateTime(), nullable=True), schema='inspection_app')

    # --- templates table ---
    op.add_column('templates', sa.Column('description', sa.Text(), nullable=True), schema='inspection_app')
    op.add_column('templates', sa.Column('version', sa.Integer(), server_default="1"), schema='inspection_app')
    op.add_column('templates', sa.Column('is_active', sa.Boolean(), server_default=sa.sql.expression.true()), schema='inspection_app')
    op.add_column('templates', sa.Column('updated_at', sa.DateTime(), nullable=True), schema='inspection_app')

    # --- template_items table ---
    op.add_column('template_items', sa.Column('description', sa.Text(), nullable=True), schema='inspection_app')
    op.add_column('template_items', sa.Column('required', sa.Boolean(), server_default=sa.sql.expression.false()), schema='inspection_app')
    op.add_column('template_items', sa.Column('order', sa.Integer(), nullable=True), schema='inspection_app')
    op.add_column('template_items', sa.Column('created_at', sa.DateTime(), nullable=True), schema='inspection_app')
    op.add_column('template_items', sa.Column('updated_at', sa.DateTime(), nullable=True), schema='inspection_app')

    # --- inspection_results table ---
    op.add_column('inspection_results', sa.Column('status', sa.String(length=20), nullable=True), schema='inspection_app')
    op.add_column('inspection_results', sa.Column('mileage', sa.Integer(), nullable=True), schema='inspection_app')
    op.add_column('inspection_results', sa.Column('location', sa.String(length=255), nullable=True), schema='inspection_app')
    op.add_column('inspection_results', sa.Column('completed_at', sa.DateTime(timezone=True), nullable=True), schema='inspection_app')
    op.add_column('inspection_results', sa.Column('updated_at', sa.DateTime(), nullable=True), schema='inspection_app')


def downgrade():
    # --- inspection_results table ---
    op.drop_column('inspection_results', 'updated_at', schema='inspection_app')
    op.drop_column('inspection_results', 'completed_at', schema='inspection_app')
    op.drop_column('inspection_results', 'location', schema='inspection_app')
    op.drop_column('inspection_results', 'mileage', schema='inspection_app')
    op.drop_column('inspection_results', 'status', schema='inspection_app')

    # --- template_items table ---
    op.drop_column('template_items', 'updated_at', schema='inspection_app')
    op.drop_column('template_items', 'created_at', schema='inspection_app')
    op.drop_column('template_items', 'order', schema='inspection_app')
    op.drop_column('template_items', 'required', schema='inspection_app')
    op.drop_column('template_items', 'description', schema='inspection_app')

    # --- templates table ---
    op.drop_column('templates', 'updated_at', schema='inspection_app')
    op.drop_column('templates', 'is_active', schema='inspection_app')
    op.drop_column('templates', 'version', schema='inspection_app')
    op.drop_column('templates', 'description', schema='inspection_app')

    # --- organizations table ---
    op.drop_column('organizations', 'updated_at', schema='inspection_app')
    op.drop_column('organizations', 'contact_name', schema='inspection_app')
    op.drop_column('organizations', 'phone_number', schema='inspection_app')
    op.drop_column('organizations', 'address', schema='inspection_app')

    # --- vehicles table ---
    op.drop_column('vehicles', 'status', schema='inspection_app')
    op.drop_column('vehicles', 'mileage', schema='inspection_app')
    op.drop_column('vehicles', 'license_plate', schema='inspection_app')
    op.drop_column('vehicles', 'vin', schema='inspection_app')
    op.drop_column('vehicles', 'year', schema='inspection_app')
    op.drop_column('vehicles', 'model', schema='inspection_app')
    op.drop_column('vehicles', 'make', schema='inspection_app')

    # --- user table ---
    op.drop_column('user', 'updated_at', schema='inspection_app')
    op.drop_column('user', 'phone_number', schema='inspection_app')
    op.drop_column('user', 'last_name', schema='inspection_app')
    op.drop_column('user', 'first_name', schema='inspection_app')