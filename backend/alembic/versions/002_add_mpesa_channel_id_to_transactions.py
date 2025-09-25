"""Add mpesa_channel_id to transactions table

Revision ID: 002_add_mpesa_channel_id_to_transactions
Revises: 001_add_mpesa_channels
Create Date: 2024-07-30 12:00:00.000000

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '002_add_mpesa_channel_id_to_transactions'
down_revision = '001_add_mpesa_channels'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Add mpesa_channel_id column to transactions table
    op.add_column('transactions', sa.Column('mpesa_channel_id', sa.Integer(), nullable=True))
    
    # Create foreign key constraint
    op.create_foreign_key(
        'fk_transactions_mpesa_channel_id', 
        'transactions', 
        'mpesa_channels', 
        ['mpesa_channel_id'], 
        ['id'], 
        ondelete='SET NULL' # Use SET NULL for existing transactions if channel is deleted
    )
    
    # Create index for the new column
    op.create_index('ix_transactions_mpesa_channel_id', 'transactions', ['mpesa_channel_id'])


def downgrade() -> None:
    # Drop index
    op.drop_index('ix_transactions_mpesa_channel_id', table_name='transactions')
    
    # Drop foreign key constraint
    op.drop_constraint('fk_transactions_mpesa_channel_id', 'transactions', type_='foreignkey')
    
    # Drop mpesa_channel_id column
    op.drop_column('transactions', 'mpesa_channel_id')