"""Initial schema

Revision ID: 001
Revises: 
Create Date: 2025-11-28

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = '001'
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Companies
    op.create_table('companies',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('name', sa.Text(), nullable=False),
        sa.Column('siret', sa.String(length=14), nullable=True),
        sa.Column('vat_number', sa.String(length=20), nullable=True),
        sa.Column('address', postgresql.JSONB(astext_type=sa.Text()), nullable=True),
        sa.Column('settings', postgresql.JSONB(astext_type=sa.Text()), nullable=True),
        sa.Column('is_active', sa.Boolean(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=True),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_companies_siret'), 'companies', ['siret'], unique=True)

    # Users
    op.create_table('users',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('company_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('email', sa.String(length=255), nullable=False),
        sa.Column('password_hash', sa.Text(), nullable=False),
        sa.Column('full_name', sa.Text(), nullable=False),
        sa.Column('role', sa.String(length=50), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=True),
        sa.ForeignKeyConstraint(['company_id'], ['companies.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_users_email'), 'users', ['email'], unique=True)

    # Customers
    op.create_table('customers',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('company_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('name', sa.Text(), nullable=False),
        sa.Column('email', sa.String(length=255), nullable=True),
        sa.Column('siret', sa.String(length=14), nullable=True),
        sa.Column('vat_number', sa.String(length=20), nullable=True),
        sa.Column('address', postgresql.JSONB(astext_type=sa.Text()), nullable=True),
        sa.Column('is_individual', sa.Boolean(), nullable=True),
        sa.Column('payment_terms', sa.Integer(), nullable=True),
        sa.ForeignKeyConstraint(['company_id'], ['companies.id'], ),
        sa.PrimaryKeyConstraint('id')
    )

    # Suppliers
    op.create_table('suppliers',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('company_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('name', sa.Text(), nullable=False),
        sa.Column('siret', sa.String(length=14), nullable=True),
        sa.Column('iban', sa.String(length=34), nullable=True),
        sa.Column('default_category', sa.String(length=50), nullable=True),
        sa.ForeignKeyConstraint(['company_id'], ['companies.id'], ),
        sa.PrimaryKeyConstraint('id')
    )

    # Invoices
    op.create_table('invoices',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('company_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('customer_id', postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column('supplier_id', postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column('type', sa.String(length=20), nullable=False),
        sa.Column('status', sa.String(length=20), nullable=False),
        sa.Column('number', sa.String(length=50), nullable=True),
        sa.Column('date_issued', sa.Date(), nullable=False),
        sa.Column('date_due', sa.Date(), nullable=False),
        sa.Column('currency', sa.CHAR(length=3), nullable=True),
        sa.Column('total_ht', sa.Numeric(precision=18, scale=2), nullable=False),
        sa.Column('total_tva', sa.Numeric(precision=18, scale=2), nullable=False),
        sa.Column('total_ttc', sa.Numeric(precision=18, scale=2), nullable=False),
        sa.Column('file_path', sa.Text(), nullable=True),
        sa.Column('facturx_xml_path', sa.Text(), nullable=True),
        sa.Column('ai_metadata', postgresql.JSONB(astext_type=sa.Text()), nullable=True),
        sa.Column('pdp_status', sa.String(length=50), nullable=True),
        sa.Column('lifecycle_status', sa.String(length=50), nullable=True),
        sa.Column('transmission_id', sa.String(length=255), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=True),
        sa.ForeignKeyConstraint(['company_id'], ['companies.id'], ),
        sa.ForeignKeyConstraint(['customer_id'], ['customers.id'], ),
        sa.ForeignKeyConstraint(['supplier_id'], ['suppliers.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_invoices_company'), 'invoices', ['company_id'], unique=False)
    op.create_index(op.f('ix_invoices_status'), 'invoices', ['status'], unique=False)
    op.create_index(op.f('ix_invoices_date_due'), 'invoices', ['date_due'], unique=False)

    # Invoice Lines
    op.create_table('invoice_lines',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('invoice_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('description', sa.Text(), nullable=False),
        sa.Column('quantity', sa.Numeric(precision=12, scale=3), nullable=True),
        sa.Column('unit_price', sa.Numeric(precision=18, scale=2), nullable=False),
        sa.Column('vat_rate', sa.Numeric(precision=5, scale=2), nullable=False),
        sa.Column('amount_ht', sa.Numeric(precision=18, scale=2), nullable=False),
        sa.ForeignKeyConstraint(['invoice_id'], ['invoices.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )

    # Transactions
    op.create_table('transactions',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('company_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('external_id', sa.String(length=255), nullable=True),
        sa.Column('date', sa.Date(), nullable=False),
        sa.Column('amount', sa.Numeric(precision=18, scale=2), nullable=False),
        sa.Column('label', sa.Text(), nullable=True),
        sa.Column('status', sa.String(length=20), nullable=True),
        sa.Column('category', sa.String(length=50), nullable=True),
        sa.ForeignKeyConstraint(['company_id'], ['companies.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_transactions_external_id'), 'transactions', ['external_id'], unique=True)

    # Payments
    op.create_table('payments',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('invoice_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('transaction_id', postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column('amount', sa.Numeric(precision=18, scale=2), nullable=False),
        sa.Column('date', sa.Date(), nullable=False),
        sa.Column('method', sa.String(length=20), nullable=True),
        sa.ForeignKeyConstraint(['invoice_id'], ['invoices.id'], ),
        sa.ForeignKeyConstraint(['transaction_id'], ['transactions.id'], ),
        sa.PrimaryKeyConstraint('id')
    )

    # Collection Cases
    op.create_table('collection_cases',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('invoice_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('status', sa.String(length=30), nullable=False),
        sa.Column('strategy', sa.String(length=30), nullable=True),
        sa.Column('next_action_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('level', sa.Integer(), nullable=True),
        sa.Column('ai_context', postgresql.JSONB(astext_type=sa.Text()), nullable=True),
        sa.ForeignKeyConstraint(['invoice_id'], ['invoices.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_collection_invoice'), 'collection_cases', ['invoice_id'], unique=True)

    # Collection Events
    op.create_table('collection_events',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('case_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('type', sa.String(length=30), nullable=False),
        sa.Column('channel', sa.String(length=20), nullable=True),
        sa.Column('content', sa.Text(), nullable=True),
        sa.Column('metadata', postgresql.JSONB(astext_type=sa.Text()), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=True),
        sa.ForeignKeyConstraint(['case_id'], ['collection_cases.id'], ),
        sa.PrimaryKeyConstraint('id')
    )




def downgrade() -> None:

    op.drop_table('collection_events')
    op.drop_table('collection_cases')
    op.drop_table('payments')
    op.drop_table('transactions')
    op.drop_table('invoice_lines')
    op.drop_table('invoices')
    op.drop_table('suppliers')
    op.drop_table('customers')
    op.drop_table('users')
    op.drop_table('companies')
