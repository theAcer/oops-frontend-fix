"""Add M-Pesa channels table for multi-tenant support

Revision ID: 001_add_mpesa_channels
Revises: 
Create Date: 2024-01-15 10:30:00.000000

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = '001_add_mpesa_channels'
down_revision = None
depends_on = None


def upgrade():
    """Create M-Pesa channels table and migrate existing data"""
    
    # Create enum types
    op.execute("CREATE TYPE channeltype AS ENUM ('paybill', 'till', 'buygoods')")
    op.execute("CREATE TYPE channelenvironment AS ENUM ('sandbox', 'production')")
    op.execute("CREATE TYPE channelstatus AS ENUM ('draft', 'configured', 'verified', 'urls_registered', 'active', 'suspended', 'error')")
    
    # Create mpesa_channels table
    op.create_table(
        'mpesa_channels',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('merchant_id', sa.Integer(), nullable=False),
        sa.Column('name', sa.String(length=100), nullable=False),
        sa.Column('shortcode', sa.String(length=20), nullable=False),
        sa.Column('channel_type', postgresql.ENUM('paybill', 'till', 'buygoods', name='channeltype'), nullable=False),
        sa.Column('environment', postgresql.ENUM('sandbox', 'production', name='channelenvironment'), nullable=False, server_default='sandbox'),
        sa.Column('consumer_key_encrypted', sa.Text(), nullable=True),
        sa.Column('consumer_secret_encrypted', sa.Text(), nullable=True),
        sa.Column('passkey_encrypted', sa.Text(), nullable=True),
        sa.Column('account_mapping', postgresql.JSONB(astext_type=sa.Text()), nullable=True),
        sa.Column('validation_url', sa.String(length=512), nullable=True),
        sa.Column('confirmation_url', sa.String(length=512), nullable=True),
        sa.Column('callback_url', sa.String(length=512), nullable=True),
        sa.Column('response_type', sa.String(length=20), nullable=False, server_default='Completed'),
        sa.Column('status', postgresql.ENUM('draft', 'configured', 'verified', 'urls_registered', 'active', 'suspended', 'error', name='channelstatus'), nullable=False, server_default='draft'),
        sa.Column('is_active', sa.Boolean(), nullable=False, server_default='true'),
        sa.Column('is_primary', sa.Boolean(), nullable=False, server_default='false'),
        sa.Column('last_verified_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('last_registration_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('verification_response', postgresql.JSONB(astext_type=sa.Text()), nullable=True),
        sa.Column('config_metadata', postgresql.JSONB(astext_type=sa.Text()), nullable=True),
        sa.Column('error_details', postgresql.JSONB(astext_type=sa.Text()), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=True),
        sa.PrimaryKeyConstraint('id')
    )
    
    # Create indexes
    op.create_index('ix_mpesa_channels_id', 'mpesa_channels', ['id'])
    op.create_index('ix_mpesa_channels_merchant_id', 'mpesa_channels', ['merchant_id'])
    op.create_index('ix_mpesa_channels_shortcode', 'mpesa_channels', ['shortcode'])
    op.create_index('ix_mpesa_channels_status', 'mpesa_channels', ['status'])
    op.create_index('ix_mpesa_channels_is_active', 'mpesa_channels', ['is_active'])
    op.create_index('ix_mpesa_channels_is_primary', 'mpesa_channels', ['is_primary'])
    
    # Create unique constraint for shortcode per merchant
    op.create_unique_constraint('uq_mpesa_channels_merchant_shortcode', 'mpesa_channels', ['merchant_id', 'shortcode'])
    
    # Create foreign key constraint
    op.create_foreign_key('fk_mpesa_channels_merchant_id', 'mpesa_channels', 'merchants', ['merchant_id'], ['id'], ondelete='CASCADE')
    
    # Add trigger for updated_at
    op.execute("""
        CREATE OR REPLACE FUNCTION update_updated_at_column()
        RETURNS TRIGGER AS $$
        BEGIN
            NEW.updated_at = now();
            RETURN NEW;
        END;
        $$ language 'plpgsql';
    """)
    
    op.execute("""
        CREATE TRIGGER update_mpesa_channels_updated_at 
        BEFORE UPDATE ON mpesa_channels 
        FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
    """)
    
    # Migrate existing M-Pesa data from merchants table (if exists)
    # This is optional and depends on your current merchant table structure
    op.execute("""
        INSERT INTO mpesa_channels (
            merchant_id, 
            name, 
            shortcode, 
            channel_type, 
            environment,
            status,
            is_primary,
            created_at
        )
        SELECT 
            id as merchant_id,
            'Legacy Channel' as name,
            COALESCE(mpesa_till_number, daraja_shortcode) as shortcode,
            CASE 
                WHEN mpesa_till_number IS NOT NULL THEN 'till'::channeltype
                ELSE 'paybill'::channeltype
            END as channel_type,
            COALESCE(daraja_environment, 'sandbox')::channelenvironment as environment,
            'draft'::channelstatus as status,
            true as is_primary,
            created_at
        FROM merchants 
        WHERE (mpesa_till_number IS NOT NULL OR daraja_shortcode IS NOT NULL)
        AND NOT EXISTS (
            SELECT 1 FROM mpesa_channels mc 
            WHERE mc.merchant_id = merchants.id
        );
    """)


def downgrade():
    """Drop M-Pesa channels table and related objects"""
    
    # Drop trigger
    op.execute("DROP TRIGGER IF EXISTS update_mpesa_channels_updated_at ON mpesa_channels;")
    op.execute("DROP FUNCTION IF EXISTS update_updated_at_column();")
    
    # Drop foreign key constraint
    op.drop_constraint('fk_mpesa_channels_merchant_id', 'mpesa_channels', type_='foreignkey')
    
    # Drop unique constraint
    op.drop_constraint('uq_mpesa_channels_merchant_shortcode', 'mpesa_channels', type_='unique')
    
    # Drop indexes
    op.drop_index('ix_mpesa_channels_is_primary', 'mpesa_channels')
    op.drop_index('ix_mpesa_channels_is_active', 'mpesa_channels')
    op.drop_index('ix_mpesa_channels_status', 'mpesa_channels')
    op.drop_index('ix_mpesa_channels_shortcode', 'mpesa_channels')
    op.drop_index('ix_mpesa_channels_merchant_id', 'mpesa_channels')
    op.drop_index('ix_mpesa_channels_id', 'mpesa_channels')
    
    # Drop table
    op.drop_table('mpesa_channels')
    
    # Drop enum types
    op.execute("DROP TYPE IF EXISTS channelstatus")
    op.execute("DROP TYPE IF EXISTS channelenvironment") 
    op.execute("DROP TYPE IF EXISTS channeltype")
