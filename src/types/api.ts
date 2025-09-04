import { BusinessType } from './enums'; // We'll create this enum soon

export interface UserResponse {
  id: number;
  email: string;
  name?: string;
  merchant_id?: number;
  is_active: boolean;
  created_at: string;
}

export interface MerchantResponse {
  id: number;
  business_name: string;
  owner_name: string;
  email: string;
  phone: string;
  business_type: BusinessType;
  mpesa_till_number: string;
  mpesa_store_number?: string;
  address?: string;
  city?: string;
  country: string;
  daraja_consumer_key?: string;
  daraja_consumer_secret?: string;
  daraja_shortcode?: string;
  daraja_passkey?: string;
  is_active: boolean;
  subscription_tier: string;
  daraaa_merchant_id?: string;
  last_sync_at?: string;
  created_at: string;
  updated_at?: string;
}

export interface TokenResponse {
  access_token: string;
  token_type: string;
}

export interface CustomerResponse {
  id: number;
  merchant_id: number;
  phone: string;
  name?: string;
  email?: string;
  customer_segment: string;
  total_spent: number;
  total_transactions: number;
  average_order_value: number;
  first_purchase_date?: string;
  last_purchase_date?: string;
  purchase_frequency_days?: number;
  loyalty_points: number;
  loyalty_tier: string;
  churn_risk_score: number;
  lifetime_value_prediction: number;
  next_purchase_prediction?: string;
  created_at: string;
  updated_at?: string;
}

export interface TransactionResponse {
  id: number;
  merchant_id: number;
  customer_id?: number;
  mpesa_receipt_number: string;
  mpesa_transaction_id?: string;
  till_number: string;
  amount: number;
  transaction_type: string; // Assuming enum from backend
  status: string; // Assuming enum from backend
  loyalty_points_earned: number;
  loyalty_processed: boolean;
  transaction_date: string;
  created_at: string;
}

export interface CampaignResponse {
  id: number;
  merchant_id: number;
  name: string;
  description?: string;
  campaign_type: string; // Assuming enum from backend
  target_audience: string; // Assuming enum from backend
  discount_percentage?: number;
  discount_amount?: number;
  points_multiplier?: number;
  minimum_spend: number;
  sms_message?: string;
  send_sms: boolean;
  status: string; // Assuming enum from backend
  custom_segment_criteria?: string;
  maximum_discount?: number;
  usage_limit_per_customer?: number;
  total_usage_limit?: number;
  current_usage_count: number;
  target_customers_count: number;
  reached_customers_count: number;
  conversion_count: number;
  total_revenue_generated: number;
  sms_sent_count: number;
  created_at: string;
  launched_at?: string;
}

export interface LoyaltyProgramResponse {
  id: number;
  merchant_id: number;
  name: string;
  description?: string;
  program_type: string; // Assuming enum from backend
  points_per_currency: number;
  minimum_spend: number;
  visits_required?: number;
  reward_visits?: number;
  bronze_threshold: number;
  silver_threshold: number;
  gold_threshold: number;
  platinum_threshold: number;
  bronze_multiplier: number;
  silver_multiplier: number;
  gold_multiplier: number;
  platinum_multiplier: number;
  is_active: boolean;
  start_date?: string;
  end_date?: string;
  created_at: string;
}

export interface NotificationHistoryItem {
  id: number;
  type: string;
  channel: string;
  recipient: string;
  message: string;
  status: string;
  sent_at?: string;
  created_at: string;
  error?: string;
}

// Request Payloads
export interface UserCreateRequest {
  email: string;
  password: string;
  name?: string;
  merchant_id?: number;
}

export interface UserLoginRequest {
  email: string;
  password: string;
}

export interface MerchantCreateRequest {
  business_name: string;
  owner_name: string;
  email: string;
  phone: string;
  business_type: BusinessType;
  mpesa_till_number: string;
  mpesa_store_number?: string;
  address?: string;
  city?: string;
  country?: string;
  daraja_consumer_key?: string;
  daraja_consumer_secret?: string;
  daraja_shortcode?: string;
  daraja_passkey?: string;
}

export interface MerchantLinkRequest {
  business_name: string;
  owner_name: string;
  email: string;
  phone: string;
  business_type: BusinessType;
  mpesa_till_number: string;
  mpesa_store_number?: string;
  address?: string;
  city?: string;
  country?: string;
  daraja_consumer_key?: string;
  daraja_consumer_secret?: string;
  daraja_shortcode?: string;
  daraja_passkey?: string;
}