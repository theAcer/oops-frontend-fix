import api from "@/lib/api"
import type {
  CustomerResponse, // Changed from Customer to CustomerResponse
  TransactionResponse, // Changed from Transaction to TransactionResponse
  MerchantResponse, // Changed from Merchant to MerchantResponse
  DashboardResponse, // Changed from DashboardAnalytics to DashboardResponse
  CampaignResponse, // Changed from Campaign to CampaignResponse
  LoyaltyProgramResponse, // Changed from LoyaltyProgram to LoyaltyProgramResponse
  NotificationHistoryItem,
  UserResponse, // Changed from AuthUser to UserResponse
  TokenResponse,
  SimulateDarajaTransactionRequest,
  MerchantCreateRequest, // Import MerchantCreateRequest
  LoyaltyProgramCreateRequest, // Import LoyaltyProgramCreateRequest
  UserCreateRequest, // Import UserCreateRequest
} from "@/types/api"

export const apiService = {
  // Auth
  async login(email: string, password: string): Promise<TokenResponse> {
    const response = await api.post("/api/v1/auth/login", { email, password })
    return response.data
  },

  async registerUser(
    email: string,
    password: string,
    name: string,
    merchantId?: number,
  ): Promise<UserResponse> {
    const response = await api.post("/api/v1/auth/register", {
      email,
      password,
      name,
      merchant_id: merchantId,
    } as UserCreateRequest) // Cast to UserCreateRequest
    return response.data
  },

  async getMe(): Promise<UserResponse> {
    const response = await api.get("/api/v1/auth/me")
    return response.data
  },

  // Dashboard Analytics
  async getDashboardAnalytics(merchantId: number): Promise<DashboardResponse> {
    const response = await api.get(`/api/v1/analytics/dashboard/${merchantId}`)
    return response.data
  },

  // Customer Management
  async getCustomers(merchantId: number, page = 1, limit = 10): Promise<{ customers: CustomerResponse[]; total: number }> {
    const response = await api.get(`/api/v1/customers?merchant_id=${merchantId}&skip=${(page - 1) * limit}&limit=${limit}`)
    return response.data
  },

  async getCustomer(customerId: number): Promise<CustomerResponse> {
    const response = await api.get(`/api/v1/customers/${customerId}`)
    return response.data
  },

  async updateCustomer(customerId: number, data: Partial<CustomerResponse>): Promise<CustomerResponse> {
    const response = await api.put(`/api/v1/customers/${customerId}`, data)
    return response.data
  },

  async getCustomerLoyalty(customerId: number): Promise<{ loyalty_points: number; loyalty_tier: string; rewards_available: number }> { // Updated return type
    const response = await api.get(`/api/v1/customers/${customerId}/loyalty`)
    return response.data
  },

  // Transaction Management
  async getTransactions(
    merchantId: number,
    filters?: { customer_id?: number; start_date?: string; end_date?: string; page?: number; limit?: number },
  ): Promise<{ transactions: TransactionResponse[]; total: number }> {
    const params = new URLSearchParams()
    params.append("merchant_id", merchantId.toString())
    if (filters?.customer_id) params.append("customer_id", filters.customer_id.toString())
    if (filters?.start_date) params.append("start_date", filters.start_date)
    if (filters?.end_date) params.append("end_date", filters.end_date)
    if (filters?.page) params.append("skip", ((filters.page - 1) * (filters.limit || 20)).toString())
    if (filters?.limit) params.append("limit", filters.limit.toString())

    const response = await api.get(`/api/v1/transactions?${params.toString()}`)
    return response.data
  },

  async getTransaction(transactionId: number): Promise<TransactionResponse> {
    const response = await api.get(`/api/v1/transactions/${transactionId}`)
    return response.data
  },

  async syncTransactions(merchantId: number): Promise<{ new_transactions: number; updated_transactions: number; total_amount: number; sync_period_start: string; sync_period_end: string }> {
    const response = await api.post(`/api/v1/transactions/sync-daraja`, { merchant_id: merchantId })
    return response.data
  },

  async simulateDarajaTransaction(data: SimulateDarajaTransactionRequest): Promise<{ message: string; transaction_id: number }> {
    const response = await api.post("/api/v1/webhooks/daraja/simulate-transaction", data);
    return response.data;
  },

  // Merchant Management
  async createMerchant(merchantData: MerchantCreateRequest): Promise<MerchantResponse> { // Use MerchantCreateRequest
    const response = await api.post("/api/v1/merchants", merchantData)
    return response.data
  },

  async linkUserToMerchant(merchantData: MerchantCreateRequest): Promise<MerchantResponse> { // Use MerchantCreateRequest
    const response = await api.post("/api/v1/merchants/link-user-merchant", merchantData)
    return response.data
  },

  async getMerchant(merchantId: number): Promise<MerchantResponse> {
    const response = await api.get(`/api/v1/merchants/${merchantId}`)
    return response.data
  },

  async updateMerchant(merchantId: number, data: Partial<MerchantResponse>): Promise<MerchantResponse> {
    const response = await api.put(`/api/v1/merchants/${merchantId}`, data)
    return response.data
  },

  // Analytics endpoints
  async getRevenueAnalytics(merchantId: number): Promise<any> {
    const response = await api.get(`/api/v1/analytics/revenue/${merchantId}`)
    return response.data
  },

  async getCustomerAnalytics(merchantId: number): Promise<any> {
    const response = await api.get(`/api/v1/analytics/customers/${merchantId}`)
    return response.data
  },

  async getLoyaltyAnalytics(merchantId: number): Promise<any> {
    const response = await api.get(`/api/v1/loyalty/analytics/${merchantId}`)
    return response.data
  },

  async getCampaignAnalytics(merchantId: number): Promise<any> {
    const response = await api.get(`/api/v1/analytics/campaigns/${merchantId}`)
    return response.data
  },

  async getCustomerInsights(merchantId: number): Promise<any> {
    const response = await api.get(`/api/v1/analytics/customer-insights/${merchantId}`)
    return response.data
  },

  async getChurnRisk(merchantId: number): Promise<any> {
    const response = await api.get(`/api/v1/analytics/churn-risk/${merchantId}`)
    return response.data
  },

  async getRevenueTrends(merchantId: number): Promise<any> {
    const response = await api.get(`/api/v1/analytics/revenue-trends/${merchantId}`)
    return response.data
  },

  async getRealTimeMetrics(merchantId: number): Promise<any> {
    const response = await api.get(`/api/v1/analytics/real-time/${merchantId}`)
    return response.data
  },

  // AI Recommendations endpoints
  async getCustomerAnalysisAI(customerId: number): Promise<any> {
    const response = await api.get(`/api/v1/ai/customer/${customerId}/analysis`)
    return response.data
  },

  async getChurnRiskAI(customerId: number): Promise<any> {
    const response = await api.get(`/api/v1/ai/customer/${customerId}/churn-risk`)
    return response.data
  },

  async getNextPurchasePrediction(customerId: number): Promise<any> {
    const response = await api.get(`/api/v1/ai/customer/${customerId}/next-purchase`)
    return response.data
  },

  async getPersonalizedOffers(customerId: number): Promise<any> {
    const response = await api.get(`/api/v1/ai/customer/${customerId}/offers`)
    return response.data
  },

  async getLifetimeValue(customerId: number): Promise<any> {
    const response = await api.get(`/api/v1/ai/customer/${customerId}/lifetime-value`)
    return response.data
  },

  async getCampaignTiming(merchantId: number): Promise<any> {
    const response = await api.get(`/api/v1/ai/merchant/${merchantId}/campaign-timing`)
    return response.data
  },

  async getMerchantInsights(merchantId: number): Promise<any> {
    const response = await api.get(`/api/v1/ai/merchant/${merchantId}/insights`)
    return response.data
  },

  async trainModels(merchantId: number): Promise<any> {
    const response = await api.post(`/api/v1/ai/merchant/${merchantId}/train-models`)
    return response.data
  },

  async getAIRecommendationsSummary(customerId: number): Promise<any> {
    const response = await api.get(`/api/v1/ai/customer/${customerId}/recommendations/summary`)
    return response.data
  },

  // Campaign Management
  async getCampaigns(merchantId: number): Promise<{ campaigns: CampaignResponse[]; total: number }> {
    const response = await api.get(`/api/v1/campaigns?merchant_id=${merchantId}`)
    return response.data
  },

  async getCampaign(campaignId: number): Promise<CampaignResponse> {
    const response = await api.get(`/api/v1/campaigns/${campaignId}`)
    return response.data
  },

  async createCampaign(campaignData: Omit<CampaignResponse, "id" | "created_at" | "status" | "custom_segment_criteria" | "maximum_discount" | "usage_limit_per_customer" | "total_usage_limit" | "current_usage_count" | "target_customers_count" | "reached_customers_count" | "conversion_count" | "total_revenue_generated" | "sms_sent_count" | "launched_at"> & { merchant_id: number; status?: string }): Promise<CampaignResponse> {
    const response = await api.post("/api/v1/campaigns", campaignData)
    return response.data
  },

  async updateCampaign(campaignId: number, data: Partial<CampaignResponse>): Promise<CampaignResponse> {
    const response = await api.put(`/api/v1/campaigns/${campaignId}`, data)
    return response.data
  },

  async launchCampaign(campaignId: number): Promise<{ message: string }> {
    const response = await api.post(`/api/v1/campaigns/${campaignId}/launch`)
    return response.data
  },

  async getCampaignPerformance(campaignId: number): Promise<any> {
    const response = await api.get(`/api/v1/campaigns/${campaignId}/performance`)
    return response.data
  },

  // Loyalty Program Management
  async getLoyaltyPrograms(merchantId: number): Promise<{ programs: LoyaltyProgramResponse[]; total: number }> {
    const response = await api.get(`/api/v1/loyalty/programs?merchant_id=${merchantId}`)
    return response.data
  },

  async getLoyaltyProgram(programId: number): Promise<LoyaltyProgramResponse> {
    const response = await api.get(`/api/v1/loyalty/programs/${programId}`)
    return response.data
  },

  async createLoyaltyProgram(programData: LoyaltyProgramCreateRequest): Promise<LoyaltyProgramResponse> {
    const response = await api.post("/api/v1/loyalty/programs", programData)
    return response.data
  },

  async updateLoyaltyProgram(programId: number, data: Partial<LoyaltyProgramResponse>): Promise<LoyaltyProgramResponse> {
    const response = await api.put(`/api/v1/loyalty/programs/${programId}`, data)
    return response.data
  },

  async activateLoyaltyProgram(programId: number): Promise<{ message: string }> {
    const response = await api.post(`/api/v1/loyalty/programs/${programId}/activate`)
    return response.data
  },

  async calculateRewards(transactionData: { transaction_id: number }): Promise<any> {
    const response = await api.post("/api/v1/loyalty/calculate-rewards", transactionData)
    return response.data
  },

  async redeemReward(rewardId: number, customerId: number): Promise<{ message: string }> {
    const response = await api.post(`/api/v1/loyalty/rewards/${rewardId}/redeem`, { customer_id: customerId })
    return response.data
  },

  async getCustomerRewards(customerId: number): Promise<any[]> {
    const response = await api.get(`/api/v1/loyalty/customers/${customerId}/rewards`)
    return response.data
  },

  // Notifications
  async sendSMS(merchantId: number, data: { phone_number: string; message: string; customer_id?: number; campaign_id?: number; notification_type?: string }): Promise<any> {
    const response = await api.post(`/api/v1/notifications/sms/send/${merchantId}`, data)
    return response.data
  },

  async sendBulkSMS(merchantId: number, data: { recipients: { phone: string; customer_id?: number; name?: string }[]; message: string; notification_type?: string; campaign_id?: number }): Promise<any> {
    const response = await api.post(`/api/v1/notifications/sms/bulk/${merchantId}`, data)
    return response.data
  },

  async sendSMSCampaign(data: {
    campaign_id: number;
    target_customers: number[];
    message_template: string;
  }): Promise<any> {
    const response = await api.post("/api/v1/notifications/sms/campaign", data)
    return response.data
  },

  async getNotificationHistory(merchantId: number, limit: number = 50): Promise<{ notifications: NotificationHistoryItem[]; count: number }> {
    const response = await api.get(`/api/v1/notifications/history/${merchantId}?limit=${limit}`)
    return response.data
  },

  async getNotificationAnalytics(merchantId: number, days: number = 30): Promise<any> {
    const response = await api.get(`/api/v1/notifications/analytics/${merchantId}?days=${days}`)
    return response.data
  },

  async getMessageTemplates(): Promise<any> {
    const response = await api.get("/api/v1/notifications/templates")
    return response.data
  },
}