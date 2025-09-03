// Merchant types
export interface Merchant {
  id: string
  business_name: string
  owner_name: string
  email: string
  phone: string
  business_type: string
  mpesa_till_number: string
  mpesa_store_number?: string
  address?: string
  city?: string
  country: string
  is_active: boolean
  subscription_tier: string
  daraaa_merchant_id?: string
  last_sync_at?: string
  created_at: string
  updated_at?: string
}

// User types for authentication
export interface AuthUser {
  id: string
  email: string
  name?: string
  merchant_id?: string
  is_active: boolean
  created_at: string
}

export interface TokenResponse {
  access_token: string
  token_type: string
}

// Customer types
export interface Customer {
  id: string
  merchant_id: string
  name: string
  email?: string
  phone: string
  total_spent: number
  loyalty_points: number
  last_visit: string // This might need to be last_purchase_date based on backend model
  created_at: string
}

// Transaction types
export interface Transaction {
  id: string
  merchant_id: string
  customer_id: string
  amount: number
  currency: string // Assuming currency is KES, but added for completeness
  status: string
  transaction_date: string
  description?: string
}

// Loyalty Program types
export interface LoyaltyProgram {
  id: string
  merchant_id: string
  name: string
  description: string
  program_type: string // e.g., "points", "visits"
  points_per_currency: number
  minimum_spend: number
  is_active: boolean
  created_at: string
}

// Campaign types
export interface Campaign {
  id: string
  merchant_id: string
  name: string
  description: string
  campaign_type: string
  target_audience: string
  status: string
  start_date: string
  end_date: string
  budget: number // This field is not in backend Campaign model, but in frontend form
  created_at: string
}

// Analytics types
export interface DashboardAnalytics {
  total_revenue: number
  total_customers: number
  total_transactions: number
  average_order_value: number
  customer_retention_rate: number
  loyalty_program_engagement: number
  revenue_growth: number
  customer_growth: number
}

// AI Recommendation types
export interface CustomerAnalysis {
  customer_id: string
  behavior_score: number
  churn_risk: number
  lifetime_value: number
  next_purchase_prediction: string
  recommended_offers: string[]
}

// Notification types
export interface NotificationHistory {
  id: string
  merchant_id: string
  recipient: string
  message: string
  status: string
  sent_at: string
  campaign_id?: string
}