from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision = '20250918_create_enum_types'
down_revision = '20250918_add_unique_index_mpesa_receipt_number' # Link to the previous migration
branch_labels = None
depends_on = None

def upgrade() -> None:
    conn = op.get_bind()
    conn.execute(sa.text("CREATE TYPE businesstype AS ENUM ('retail', 'service', 'hospitality', 'other')"))
    conn.execute(sa.text("CREATE TYPE subscriptiontier AS ENUM ('basic', 'premium', 'enterprise')"))

def downgrade() -> None:
    conn = op.get_bind()
    conn.execute(sa.text("DROP TYPE IF EXISTS businesstype"))
    conn.execute(sa.text("DROP TYPE IF EXISTS subscriptiontier")) 