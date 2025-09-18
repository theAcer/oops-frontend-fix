from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision = '20250918_add_unique_index_mpesa_receipt_number'
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Create unique constraint/index if not exists
    conn = op.get_bind()
    # Create index with IF NOT EXISTS (PostgreSQL 9.5+ supports it for indexes)
    conn.execute(sa.text('CREATE UNIQUE INDEX IF NOT EXISTS ux_transactions_mpesa_receipt_number ON transactions (mpesa_receipt_number)'))


def downgrade() -> None:
    conn = op.get_bind()
    conn.execute(sa.text('DROP INDEX IF EXISTS ux_transactions_mpesa_receipt_number')) 