import api from "@/lib/api"
import type {
  Customer,
  Transaction,
  Merchant,
  DashboardAnalytics,
  Campaign,
  LoyaltyProgram,
  NotificationHistory,
} from "@/types/api"

export const apiService = {
  // Dashboard Analytics
  async getDashboardAnalytics(merchantId: string): Promise<DashboardAnalytics> {
    const response = await api.get(`/analytics/dashboard/${merchantId}`)
    return response.data
  },

  // Customer Management
  async getCustomers(merchantId: string, page = 1, limit = 10): Promise<{ customers: Customer[]; total: number }> {
    const response = await api.get(`/customers?merchant_id=${merchantId}&page=${page}&limit=${limit}`)
    return response.data
  },

  async getCustomer(customerId: string): Promise<Customer> {
    const response = await api.get(`/customers/${customerId}`)
    return response.data
  },

  async updateCustomer(customerId: string, data: Partial<Customer>): Promise<Customer> {
    const response = await api.put(`/customers/${customerId}`, data)
    return response.data
  },

  async getCustomerLoyalty(customerId: string): Promise<{ points: number; tier: string; rewards: any[] }> {
    const response = await api.get(`/customers/${customerId}/loyalty`)
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
    if (filters?.page) params.append("page", filters.page.toString())
    if (filters?.limit) params.append("limit", filters.limit.toString())

    const response = await api.get(`/transactions?${params.toString()}`)
    return response.data
  },

  async getTransaction(transactionId: string): Promise<Transaction> {
    const response = await api.get(`/transactions/${transactionId}`)
    return response.data
  },

  async syncTransactions(merchantId: string): Promise<{ synced: number; message: string }> {
    const response = await api.post(`/transactions/sync`, { merchant_id: merchantId })
    return response.data
  },

  // Merchant Management
  async getMerchant(merchantId: string): Promise<Merchant> {
    const response = await api.get(`/merchants/${merchantId}`)
    return response.data
  },

  async updateMerchant(merchantId: string, data: Partial<Merchant>): Promise<Merchant> {
    const response = await api.put(`/merchants/${merchantId}`, data)
    return response.data
  },

  // Analytics endpoints
  async getRevenueAnalytics(merchantId: string): Promise<any> {
    const response = await api.get(`/analytics/revenue/${merchantId}`)
    return response.data
  },

  async getCustomerAnalytics(merchantId: string): Promise<any> {
    const response = await api.get(`/analytics/customers/${merchantId}`)
    return response.data
  },

  async getLoyaltyAnalytics(merchantId: string): Promise<any> {
    const response = await api.get(`/analytics/loyalty/${merchantId}`)
    return response.data
  },

  async getCampaignAnalytics(merchantId: string): Promise<any> {
    const response = await api.get(`/analytics/campaigns/${merchantId}`)
    return response.data
  },

  async getCustomerInsights(merchantId: string): Promise<any> {
    const response = await api.get(`/analytics/customer-insights/${merchantId}`)
    return response.data
  },

  async getChurnRisk(merchantId: string): Promise<any> {
    const response = await api.get(`/analytics/churn-risk/${merchantId}`)
    return response.data
  },

  async getRevenueTrends(merchantId: string): Promise<any> {
    const response = await api.get(`/analytics/revenue-trends/${merchantId}`)
    return response.data
  },

  async getRealTimeMetrics(merchantId: string): Promise<any> {
    const response = await api.get(`/analytics/real-time/${merchantId}`)
    return response.data
  },

  // AI Recommendations endpoints
  async getCustomerAnalysisAI(customerId: string): Promise<any> {
    const response = await api.get(`/ai/customer/${customerId}/analysis`)
    return response.data
  },

  async getChurnRiskAI(customerId: string): Promise<any> {
    const response = await api.get(`/ai/customer/${customerId}/churn-risk`)
    return response.data
  },

  async getNextPurchasePrediction(customerId: string): Promise<any> {
    const response = await api.get(`/ai/customer/${customerId}/next-purchase`)
    return response.data
  },

  async getPersonalizedOffers(customerId: string): Promise<any> {
    const response = await api.get(`/ai/customer/${customerId}/offers`)
    return response.data
  },

  async getLifetimeValue(customerId: string): Promise<any> {
    const response = await api.get(`/ai/customer/${customerId}/lifetime-value`)
    return response.data
  },

  async getCampaignTiming(merchantId: string): Promise<any> {
    const response = await api.get(`/ai/merchant/${merchantId}/campaign-timing`)
    return response.data
  },

  async getMerchantInsights(merchantId: string): Promise<any> {
    const response = await api.get(`/ai/merchant/${merchantId}/insights`)
    return response.data
  },

  async trainModels(merchantId: string): Promise<any> {
    const response = await api.post(`/ai/merchant/${merchantId}/train-models`)
    return response.data
  },

  async getAIRecommendationsSummary(customerId: string): Promise<any> {
    const response = await api.get(`/ai/customer/${customerId}/recommendations/summary`)
    return response.data
  },

  // Campaign Management
  async getCampaigns(merchantId: string): Promise<{ campaigns: Campaign[]; total: number }> {
    const response = await api.get(`/campaigns?merchant_id=${merchantId}`)
    return response.data
  },

  async getCampaign(campaignId: string): Promise<Campaign> {
    const response = await api.get(`/campaigns/${campaignId}`)
    return response.data
  },

  async createCampaign(campaignData: Omit<Campaign, "id" | "created_at">): Promise<Campaign> {
    const response = await api.post("/campaigns", campaignData)
    return response.data
  },

  async updateCampaign(campaignId: string, data: Partial<Campaign>): Promise<Campaign> {
    const response = await api.put(`/campaigns/${campaignId}`, data)
    return response.data
  },

  async launchCampaign(campaignId: string): Promise<{ message: string }> {
    const response = await api.post(`/campaigns/${campaignId}/launch`)
    return response.data
  },

  async getCampaignPerformance(campaignId: string): Promise<any> {
    const response = await api.get(`/campaigns/${campaignId}/performance`)
    return response.data
  },

  // Loyalty Program Management
  async getLoyaltyPrograms(merchantId: string): Promise<{ programs: LoyaltyProgram[]; total: number }> {
    const response = await api.get(`/loyalty/programs?merchant_id=${merchantId}`)
    return response.data
  },

  async getLoyaltyProgram(programId: string): Promise<LoyaltyProgram> {
    const response = await api.get(`/loyalty/programs/${programId}`)
    return response.data
  },

  async createLoyaltyProgram(programData: Omit<LoyaltyProgram, "id" | "created_at">): Promise<LoyaltyProgram> {
    const response = await api.post("/loyalty/programs", programData)
    return response.data
  },

  async updateLoyaltyProgram(programId: string, data: Partial<LoyaltyProgram>): Promise<LoyaltyProgram> {
    const response = await api.put(`/loyalty/programs/${programId}`, data)
    return response.data
  },

  async activateLoyaltyProgram(programId: string): Promise<{ message: string }> {
    const response = await api.post(`/loyalty/programs/${programId}/activate`)
    return response.data
  },

  async calculateRewards(transactionData: { transaction_id: string; program_id: string }): Promise<any> {
    const response = await api.post("/loyalty/calculate-rewards", transactionData)
    return response.data
  },

  async redeemReward(rewardId: string): Promise<{ message: string }> {
    const response = await api.post(`/loyalty/rewards/${rewardId}/redeem`)
    return response.data
  },

  async getCustomerRewards(customerId: string): Promise<any[]> {
    const response = await api.get(`/loyalty/customers/${customerId}/rewards`)
    return response.data
  },

  // Notifications
  async sendSMS(merchantId: string, data: { recipient: string; message: string }): Promise<any> {
    const response = await api.post(`/notifications/sms/send/${merchantId}`, data)
    return response.data
  },

  async sendBulkSMS(merchantId: string, data: { recipients: string[]; message: string }): Promise<any> {
    const response = await api.post(`/notifications/sms/bulk/${merchantId}`, data)
    return response.data
  },

  async sendSMSCampaign(data: {
    merchant_id: string
    campaign_id: string
    target_audience: string
    message: string
  }): Promise<any> {
    const response = await api.post("/notifications/sms/campaign", data)
    return response.data
  },

  async getNotificationHistory(merchantId: string): Promise<{ notifications: NotificationHistory[]; total: number }> {
    const response = await api.get(`/notifications/history/${merchantId}`)
    return response.data
  },

  async getNotificationAnalytics(merchantId: string): Promise<any> {
    const response = await api.get(`/notifications/analytics/${merchantId}`)
    return response.data
  },

  async getMessageTemplates(): Promise<any[]> {
    const response = await api.get("/notifications/templates")
    return response.data
  },
}
