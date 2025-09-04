import api from "@/lib/api"
import type {
  Customer,
  Transaction,
  Merchant,
  DashboardAnalytics,
  Campaign,
  LoyaltyProgram,
  NotificationHistory,
  AuthUser,
  TokenResponse,
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
    merchantId?: string, // Made optional
  ): Promise<AuthUser> {
    const response = await api.post("/api/v1/auth/register", {
      email,
      password,
      name,
      merchant_id: merchantId,
    })
    return response.data
  },

  async getMe(): Promise<AuthUser> {
    const response = await api.get("/api/v1/auth/me")
    return response.data
  },

  // Dashboard Analytics
  async getDashboardAnalytics(merchantId: string): Promise<DashboardAnalytics> {
    const response = await api.get(`/api/v1/analytics/dashboard/${merchantId}`)
    return response.data
  },

  // Customer Management
  async getCustomers(merchantId: string, page = 1, limit = 10): Promise<{ customers: Customer[]; total: number }> {
    const response = await api.get(`/api/v1/customers?merchant_id=${merchantId}&skip=${(page - 1) * limit}&limit=${limit}`)
    return response.data
  },

  async getCustomer(customerId: string): Promise<Customer> {
    const response = await api.get(`/api/v1/customers/${customerId}`)
    return response.data
  },

  async updateCustomer(customerId: string, data: Partial<Customer>): Promise<Customer> {
    const response = await api.put(`/api/v1/customers/${customerId}`, data)
    return response.data
  },

  async getCustomerLoyalty(customerId: string): Promise<{ points: number; tier: string; rewards: any[] }> {
    const response = await api.get(`/api/v1/customers/${customerId}/loyalty`)
    return response.data
  },

  // Transaction Management
  async getTransactions(
    merchantId: string,
    filters?: { customer_id?: string; start_date?: string; end_date?: string; page?: number; limit?: number },
  ): Promise<{ transactions: Transaction[]; total: number }> {
    const params = new URLSearchParams()
    params.append("merchant_id", merchantId)
    if (filters?.customer_id) params.append("customer_id", filters.customer_id)
    if (filters?.start_date) params.append("start_date", filters.start_date)
    if (filters?.end_date) params.append("end_date", filters.end_date)
    if (filters?.page) params.append("skip", ((filters.page - 1) * (filters.limit || 20)).toString())
    if (filters?.limit) params.append("limit", filters.limit.toString())

    const response = await api.get(`/api/v1/transactions?${params.toString()}`)
    return response.data
  },

  async getTransaction(transactionId: string): Promise<Transaction> {
    const response = await api.get(`/api/v1/transactions/${transactionId}`)
    return response.data
  },

  async syncTransactions(merchantId: string): Promise<{ synced: number; message: string }> {
    // Changed to call the new Daraja sync endpoint
    const response = await api.post(`/api/v1/transactions/sync-daraja`, { merchant_id: merchantId })
    return response.data
  },

  // Merchant Management
  async createMerchant(merchantData: Omit<Merchant, "id" | "created_at" | "updated_at" | "is_active" | "subscription_tier" | "daraaa_merchant_id" | "last_sync_at">): Promise<Merchant> {
    const response = await api.post("/api/v1/merchants", merchantData)
    return response.data
  },

  async linkUserToMerchant(merchantData: Omit<Merchant, "id" | "created_at" | "updated_at" | "is_active" | "subscription_tier" | "daraaa_merchant_id" | "last_sync_at">): Promise<Merchant> {
    const response = await api.post("/api/v1/merchants/link-user-merchant", merchantData)
    return response.data
  },

  async getMerchant(merchantId: string): Promise<Merchant> {
    const response = await api.get(`/api/v1/merchants/${merchantId}`)
    return response.data
  },

  async updateMerchant(merchantId: string, data: Partial<Merchant>): Promise<Merchant> {
    const response = await api.put(`/api/v1/merchants/${merchantId}`, data)
    return response.data
  },

  // Analytics endpoints
  async getRevenueAnalytics(merchantId: string): Promise<any> {
    const response = await api.get(`/api/v1/analytics/revenue/${merchantId}`)
    return response.data
  },

  async getCustomerAnalytics(merchantId: string): Promise<any> {
    const response = await api.get(`/api/v1/analytics/customers/${merchantId}`)
    return response.data
  },

  async getLoyaltyAnalytics(merchantId: string): Promise<any> {
    const response = await api.get(`/api/v1/analytics/loyalty/${merchantId}`)
    return response.data
  },

  async getCampaignAnalytics(merchantId: string): Promise<any> {
    const response = await api.get(`/api/v1/analytics/campaigns/${merchantId}`)
    return response.data
  },

  async getCustomerInsights(merchantId: string): Promise<any> {
    const response = await api.get(`/api/v1/analytics/customer-insights/${merchantId}`)
    return response.data
  },

  async getChurnRisk(merchantId: string): Promise<any> {
    const response = await api.get(`/api/v1/analytics/churn-risk/${merchantId}`)
    return response.data
  },

  async getRevenueTrends(merchantId: string): Promise<any> {
    const response = await api.get(`/api/v1/analytics/revenue-trends/${merchantId}`)
    return response.data
  },

  async getRealTimeMetrics(merchantId: string): Promise<any> {
    const response = await api.get(`/api/v1/analytics/real-time/${merchantId}`)
    return response.data
  },

  // AI Recommendations endpoints
  async getCustomerAnalysisAI(customerId: string): Promise<any> {
    const response = await api.get(`/api/v1/ai/customer/${customerId}/analysis`)
    return response.data
  },

  async getChurnRiskAI(customerId: string): Promise<any> {
    const response = await api.get(`/api/v1/ai/customer/${customerId}/churn-risk`)
    return response.data
  },

  async getNextPurchasePrediction(customerId: string): Promise<any> {
    const response = await api.get(`/api/v1/ai/customer/${customerId}/next-purchase`)
    return response.data
  },

  async getPersonalizedOffers(customerId: string): Promise<any> {
    const response = await api.get(`/api/v1/ai/customer/${customerId}/offers`)
    return response.data
  },

  async getLifetimeValue(customerId: string): Promise<any> {
    const response = await api.get(`/api/v1/ai/customer/${customerId}/lifetime-value`)
    return response.data
  },

  async getCampaignTiming(merchantId: string): Promise<any> {
    const response = await api.get(`/api/v1/ai/merchant/${merchantId}/campaign-timing`)
    return response.data
  },

  async getMerchantInsights(merchantId: string): Promise<any> {
    const response = await api.get(`/api/v1/ai/merchant/${merchantId}/insights`)
    return response.data
  },

  async trainModels(merchantId: string): Promise<any> {
    const response = await api.post(`/api/v1/ai/merchant/${merchantId}/train-models`)
    return response.data
  },

  async getAIRecommendationsSummary(customerId: string): Promise<any> {
    const response = await api.get(`/api/v1/ai/customer/${customerId}/recommendations/summary`)
    return response.data
  },

  // Campaign Management
  async getCampaigns(merchantId: string): Promise<{ campaigns: Campaign[]; total: number }> {
    const response = await api.get(`/api/v1/campaigns?merchant_id=${merchantId}`)
    return response.data
  },

  async getCampaign(campaignId: string): Promise<Campaign> {
    const response = await api.get(`/api/v1/campaigns/${campaignId}`)
    return response.data
  },

  async createCampaign(campaignData: Omit<Campaign, "id" | "created_at">): Promise<Campaign> {
    const response = await api.post("/api/v1/campaigns", campaignData)
    return response.data
  },

  async updateCampaign(campaignId: string, data: Partial<Campaign>): Promise<Campaign> {
    const response = await api.put(`/api/v1/campaigns/${campaignId}`, data)
    return response.data
  },

  async launchCampaign(campaignId: string): Promise<{ message: string }> {
    const response = await api.post(`/api/v1/campaigns/${campaignId}/launch`)
    return response.data
  },

  async getCampaignPerformance(campaignId: string): Promise<any> {
    const response = await api.get(`/api/v1/campaigns/${campaignId}/performance`)
    return response.data
  },

  // Loyalty Program Management
  async getLoyaltyPrograms(merchantId: string): Promise<{ programs: LoyaltyProgram[]; total: number }> {
    const response = await api.get(`/api/v1/loyalty/programs?merchant_id=${merchantId}`)
    return response.data
  },

  async getLoyaltyProgram(programId: string): Promise<LoyaltyProgram> {
    const response = await api.get(`/api/v1/loyalty/programs/${programId}`)
    return response.data
  },

  async createLoyaltyProgram(programData: Omit<LoyaltyProgram, "id" | "created_at">): Promise<LoyaltyProgram> {
    const response = await api.post("/api/v1/loyalty/programs", programData)
    return response.data
  },

  async updateLoyaltyProgram(programId: string, data: Partial<LoyaltyProgram>): Promise<LoyaltyProgram> {
    const response = await api.put(`/api/v1/loyalty/programs/${programId}`, data)
    return response.data
  },

  async activateLoyaltyProgram(programId: string): Promise<{ message: string }> {
    const response = await api.post(`/api/v1/loyalty/programs/${programId}/activate`)
    return response.data
  },

  async calculateRewards(transactionData: { transaction_id: string; program_id: string }): Promise<any> {
    const response = await api.post("/api/v1/loyalty/calculate-rewards", transactionData)
    return response.data
  },

  async redeemReward(rewardId: string): Promise<{ message: string }> {
    const response = await api.post(`/api/v1/loyalty/rewards/${rewardId}/redeem`)
    return response.data
  },

  async getCustomerRewards(customerId: string): Promise<any[]> {
    const response = await api.get(`/api/v1/loyalty/customers/${customerId}/rewards`)
    return response.data
  },

  // Notifications
  async sendSMS(merchantId: string, data: { recipient: string; message: string }): Promise<any> {
    const response = await api.post(`/api/v1/notifications/sms/send/${merchantId}`, data)
    return response.data
  },

  async sendBulkSMS(merchantId: string, data: { recipients: string[]; message: string }): Promise<any> {
    const response = await api.post(`/api/v1/notifications/sms/bulk/${merchantId}`, data)
    return response.data
  },

  async sendSMSCampaign(data: {
    campaign_id: string
    target_customers: number[]
    message_template: string
  }): Promise<any> {
    const response = await api.post("/api/v1/notifications/sms/campaign", data)
    return response.data
  },

  async getNotificationHistory(merchantId: string): Promise<{ notifications: NotificationHistory[]; total: number }> {
    const response = await api.get(`/api/v1/notifications/history/${merchantId}`)
    return response.data
  },

  async getNotificationAnalytics(merchantId: string): Promise<any> {
    const response = await api.get(`/api/v1/notifications/analytics/${merchantId}`)
    return response.data
  },

  async getMessageTemplates(): Promise<any[]> {
    const response = await api.get("/api/v1/notifications/templates")
    return response.data
  },
}