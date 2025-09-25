# 🚀 **Multi-Tenant M-Pesa Integration Guide**

## 🎯 **The Problem You Identified**

You're absolutely right! The previous approach was **fundamentally broken** for a multi-tenant loyalty platform:

❌ **Old Broken Approach:**
- Single M-Pesa credentials in `.env` file
- Can't handle multiple merchants
- No support for multiple till numbers per merchant
- No account number differentiation for PayBills
- Not scalable for a SaaS platform

✅ **New Multi-Tenant Solution:**
- **Per-merchant M-Pesa credentials** with secure encryption
- **Multiple channels per merchant** (Till, PayBill, Buy Goods)
- **Account number mapping** for PayBill differentiation
- **Secure credential storage** with encryption at rest
- **Easy merchant onboarding** with step-by-step flow

## 🏗️ **New Architecture Overview**

### **Database Structure:**
```sql
-- Each merchant can have multiple M-Pesa channels
mpesa_channels:
├── id (Primary Key)
├── merchant_id (Foreign Key to merchants)
├── name (e.g., "Main PayBill", "Shop Till")
├── shortcode (M-Pesa shortcode)
├── channel_type (paybill|till|buygoods)
├── environment (sandbox|production)
├── consumer_key_encrypted (Encrypted credentials)
├── consumer_secret_encrypted (Encrypted credentials)
├── passkey_encrypted (For STK Push)
├── account_mapping (JSON: {"VIP*": "vip_account"})
├── status (draft|configured|verified|active)
├── is_primary (Boolean: primary channel)
└── ... (URLs, metadata, timestamps)
```

### **Multi-Channel Support:**
```json
{
  "merchant_123": {
    "channels": [
      {
        "id": 1,
        "name": "Main PayBill",
        "shortcode": "174379",
        "type": "paybill",
        "account_mapping": {
          "default": "loyalty",
          "VIP*": "vip_account",
          "GOLD001": "gold_tier"
        }
      },
      {
        "id": 2,
        "name": "Shop Till",
        "shortcode": "123456",
        "type": "till"
      }
    ]
  }
}
```

## 🔐 **Security Implementation**

### **Credential Encryption:**
```python
# Credentials are NEVER stored in plain text
class MpesaChannel(Base):
    consumer_key_encrypted = Column(Text, nullable=True)
    consumer_secret_encrypted = Column(Text, nullable=True)
    
    @hybrid_property
    def consumer_key(self) -> Optional[str]:
        """Decrypt and return consumer key"""
        if self.consumer_key_encrypted:
            return decrypt_data(self.consumer_key_encrypted)
        return None
    
    @consumer_key.setter
    def consumer_key(self, value: Optional[str]):
        """Encrypt and store consumer key"""
        if value:
            self.consumer_key_encrypted = encrypt_data(value)
```

### **Environment Variables (Updated):**
```bash
# Single encryption key for all merchant credentials
ENCRYPTION_KEY=your_32_character_encryption_key_here

# Remove these - no longer needed!
# MPESA_CONSUMER_KEY=...
# MPESA_CONSUMER_SECRET=...
```

## 📋 **Merchant Onboarding Flow**

### **Step 1: Merchant Registration**
```typescript
// Frontend: Merchant signs up for the loyalty platform
const merchantData = {
  business_name: "Acme Electronics",
  owner_name: "John Doe",
  email: "john@acme.com",
  phone: "254712345678",
  business_type: "RETAIL"
}
```

### **Step 2: M-Pesa Channel Setup**
```typescript
// Merchant adds their first M-Pesa channel
const channelData = {
  name: "Main PayBill",
  shortcode: "174379",
  channel_type: "paybill",
  environment: "sandbox", // Start with sandbox
  consumer_key: "merchant_provided_key",
  consumer_secret: "merchant_provided_secret",
  passkey: "merchant_provided_passkey",
  account_mapping: {
    "default": "loyalty",
    "VIP*": "vip_customers",
    "PREMIUM": "premium_tier"
  }
}
```

### **Step 3: Channel Verification**
```typescript
// System verifies channel with Safaricom
POST /api/v1/mpesa-channels/{channel_id}/verify

// Response:
{
  "verified": true,
  "status": "verified",
  "verification_details": {
    "shortcode": "174379",
    "account_balance_accessible": true,
    "verified_at": "2024-01-15T10:30:00Z"
  }
}
```

### **Step 4: URL Registration**
```typescript
// Register callback URLs for C2B transactions
POST /api/v1/mpesa-channels/{channel_id}/register-urls

{
  "validation_url": "https://merchant-api.com/mpesa/validation",
  "confirmation_url": "https://merchant-api.com/mpesa/confirmation",
  "response_type": "Completed"
}
```

### **Step 5: Channel Activation**
```typescript
// Activate channel for live transactions
POST /api/v1/mpesa-channels/{channel_id}/activate

// Channel is now ready for loyalty program integration!
```

## 🎛️ **API Usage Examples**

### **Create Multiple Channels:**
```typescript
// PayBill Channel
const paybillChannel = await createChannel({
  name: "Customer PayBill",
  shortcode: "174379",
  channel_type: "paybill",
  account_mapping: {
    "default": "loyalty",
    "VIP*": "vip_tier",
    "STUDENT*": "student_discount"
  }
});

// Till Channel  
const tillChannel = await createChannel({
  name: "Shop Till",
  shortcode: "123456", 
  channel_type: "till"
});

// Buy Goods Channel
const buygoodsChannel = await createChannel({
  name: "Online Store",
  shortcode: "789012",
  channel_type: "buygoods"
});
```

### **Account Mapping for PayBills:**
```typescript
// Different account references route to different loyalty programs
const accountMapping = {
  "default": "standard_loyalty",      // Default customers
  "VIP*": "vip_program",             // VIP001, VIP002, etc.
  "STUDENT*": "student_program",      // STUDENT001, etc.
  "CORPORATE": "b2b_program",         // Exact match
  "GOLD*": "gold_tier",              // GOLD001, GOLD002, etc.
}

// When customer pays with reference "VIP001":
// → Routes to "vip_program" loyalty account
// → Different point rates, rewards, etc.
```

### **Transaction Processing:**
```typescript
// Incoming M-Pesa transaction
const transaction = {
  shortcode: "174379",
  amount: 1000,
  customer_phone: "254712345678",
  bill_ref: "VIP001",
  transaction_id: "ABC123DEF456"
};

// System automatically:
// 1. Identifies merchant by shortcode
// 2. Maps "VIP001" to "vip_program" using account_mapping
// 3. Awards loyalty points based on VIP tier rules
// 4. Sends personalized SMS to customer
```

## 🚀 **Implementation Benefits**

### **For the Platform (You):**
- ✅ **True Multi-Tenancy**: Each merchant has isolated M-Pesa setup
- ✅ **Scalable Architecture**: Add unlimited merchants and channels
- ✅ **Security**: Encrypted credentials, no shared secrets
- ✅ **Flexibility**: Support any M-Pesa channel type
- ✅ **Maintainable**: Clean separation of concerns

### **For Merchants:**
- ✅ **Own Their Data**: Use their own M-Pesa credentials
- ✅ **Multiple Channels**: PayBill + Till + Buy Goods
- ✅ **Account Segmentation**: Different customer tiers via account mapping
- ✅ **Easy Setup**: Step-by-step onboarding flow
- ✅ **Full Control**: Activate/deactivate channels as needed

### **For Customers:**
- ✅ **Seamless Experience**: Pay to any merchant channel
- ✅ **Automatic Recognition**: System knows which loyalty program
- ✅ **Personalized Rewards**: Based on account tier/segment
- ✅ **Consistent Service**: Same experience across all channels

## 📊 **Real-World Use Cases**

### **Case 1: Electronics Store Chain**
```typescript
const acmeElectronics = {
  merchant_id: 123,
  channels: [
    {
      name: "Main Store PayBill",
      shortcode: "174379",
      type: "paybill",
      account_mapping: {
        "default": "standard_customer",
        "VIP*": "vip_customer",
        "STAFF*": "employee_discount",
        "WHOLESALE": "b2b_customer"
      }
    },
    {
      name: "Online Store Till",
      shortcode: "555123",
      type: "till"
    },
    {
      name: "Repair Services",
      shortcode: "555456", 
      type: "buygoods"
    }
  ]
}

// Customer pays:
// PayBill 174379, Account: VIP001, Amount: 5000
// → VIP loyalty program
// → 2x points (VIP multiplier)
// → SMS: "Hi John! You earned 100 VIP points. Total: 2,847 points."
```

### **Case 2: Restaurant Chain**
```typescript
const tasteRestaurants = {
  merchant_id: 456,
  channels: [
    {
      name: "Westlands Branch",
      shortcode: "200100",
      type: "till"
    },
    {
      name: "CBD Branch", 
      shortcode: "200200",
      type: "till"
    },
    {
      name: "Delivery Service",
      shortcode: "200300",
      type: "paybill",
      account_mapping: {
        "default": "dine_in",
        "DELIVERY": "delivery_customer",
        "CATERING": "catering_service"
      }
    }
  ]
}

// Customer orders delivery:
// PayBill 200300, Account: DELIVERY, Amount: 1200
// → Delivery loyalty program
// → Free delivery after 5 orders
// → SMS: "Thanks for ordering! 4 more orders for free delivery."
```

## 🔧 **Migration from Old System**

### **Step 1: Environment Variables**
```bash
# OLD (remove these)
MPESA_CONSUMER_KEY=single_key_for_all
MPESA_CONSUMER_SECRET=single_secret_for_all

# NEW (add this)
ENCRYPTION_KEY=XoX9omKWv1dfP6s2FVpz4P-12bL7_7ysy1Gf1YtjZjk=
```

### **Step 2: Database Migration**
```sql
-- Create new mpesa_channels table
CREATE TABLE mpesa_channels (
    id SERIAL PRIMARY KEY,
    merchant_id INTEGER REFERENCES merchants(id) ON DELETE CASCADE,
    name VARCHAR(100) NOT NULL,
    shortcode VARCHAR(20) NOT NULL,
    channel_type VARCHAR(20) NOT NULL,
    environment VARCHAR(20) DEFAULT 'sandbox',
    consumer_key_encrypted TEXT,
    consumer_secret_encrypted TEXT,
    passkey_encrypted TEXT,
    account_mapping JSONB,
    status VARCHAR(50) DEFAULT 'draft',
    is_active BOOLEAN DEFAULT TRUE,
    is_primary BOOLEAN DEFAULT FALSE,
    -- ... other fields
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE
);

-- Migrate existing merchant data
INSERT INTO mpesa_channels (merchant_id, name, shortcode, channel_type, ...)
SELECT id, 'Legacy Channel', mpesa_till_number, 'till', ...
FROM merchants 
WHERE mpesa_till_number IS NOT NULL;
```

### **Step 3: Code Updates**
```python
# OLD approach
mpesa_service = MpesaService(
    consumer_key=settings.MPESA_CONSUMER_KEY,  # Single key for all
    consumer_secret=settings.MPESA_CONSUMER_SECRET
)

# NEW approach  
async def get_merchant_mpesa_service(merchant_id: int, channel_id: int):
    channel = await get_mpesa_channel(merchant_id, channel_id)
    credentials = channel.get_credentials_dict()
    
    return MpesaServiceFactory.create_transaction_service(**credentials)
```

## 🎯 **Next Steps**

### **Immediate (High Priority):**
1. ✅ **Enhanced M-Pesa Channel Model** - Done!
2. ✅ **Secure Credential Encryption** - Done!
3. ✅ **Multi-Channel API Endpoints** - Done!
4. 🔄 **Database Migration Script** - In Progress
5. ⏳ **Frontend Onboarding Flow** - Next

### **Short Term (Medium Priority):**
1. **Merchant Dashboard**: Channel management UI
2. **Webhook Handlers**: Process M-Pesa callbacks per channel
3. **Account Mapping UI**: Visual account reference setup
4. **Channel Health Monitoring**: Status dashboard
5. **Bulk Operations**: Import/export channel configurations

### **Long Term (Low Priority):**
1. **Advanced Analytics**: Per-channel transaction insights
2. **A/B Testing**: Different loyalty rules per channel
3. **Channel Automation**: Auto-activate based on verification
4. **Integration Templates**: Pre-built configurations for common setups
5. **White-label Options**: Custom branding per merchant

## 🎉 **Summary**

Your instinct was **100% correct**! The old single-credential approach was completely unsuitable for a multi-tenant loyalty platform. 

The new architecture provides:

🏢 **True Multi-Tenancy**: Each merchant manages their own M-Pesa integration  
🔐 **Enterprise Security**: Encrypted credentials, isolated data  
📈 **Unlimited Scalability**: Support thousands of merchants and channels  
🎯 **Business Flexibility**: Multiple channels, account mapping, tier management  
🚀 **Easy Onboarding**: Step-by-step merchant setup flow  

This is now a **proper SaaS loyalty platform** that can scale to serve multiple merchants with their own M-Pesa integrations! 🎊
