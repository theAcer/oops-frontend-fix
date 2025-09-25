import api from "@/lib/api"
import type { 
  MerchantResponse, 
  MerchantCreateRequest,
  LoyaltyProgramResponse,
  LoyaltyProgramCreateRequest
} from "@/types/api"
import type { BusinessInfo, MpesaChannelData, LoyaltyProgramConfig } from "@/contexts/onboarding-context"

export interface OnboardingMerchantRequest extends MerchantCreateRequest {
  business_address?: string
  business_description?: string
  website?: string
  tax_id?: string
}

export interface OnboardingMpesaChannelRequest {
  name: string
  shortcode: string
  channel_type: "paybill" | "till" | "buygoods"
  environment: "sandbox" | "production"
  consumer_key: string
  consumer_secret: string
  passkey?: string
  validation_url?: string
  confirmation_url?: string
  callback_url?: string
  account_mapping?: Record<string, string>
  is_primary: boolean
}

export interface OnboardingLoyaltyProgramRequest extends LoyaltyProgramCreateRequest {
  tier_system_enabled: boolean
  tiers?: {
    name: string
    min_points: number
    multiplier: number
    benefits: string[]
  }[]
  welcome_bonus: number
  referral_bonus: number
  birthday_bonus: number
}

export interface ChannelVerificationResult {
  channel_id: number
  verified: boolean
  status: string
  verification_details?: any
  error?: string
}

export interface OnboardingResult {
  merchant: MerchantResponse
  channels: any[]
  loyalty_program: LoyaltyProgramResponse
  verification_results: ChannelVerificationResult[]
}

export const onboardingService = {
  /**
   * Create merchant account from business info
   */
  async createMerchant(businessInfo: BusinessInfo): Promise<MerchantResponse> {
    const merchantData: OnboardingMerchantRequest = {
      business_name: businessInfo.businessName,
      owner_name: businessInfo.ownerName,
      email: businessInfo.email,
      phone: businessInfo.phone,
      business_type: businessInfo.businessType.toUpperCase(),
      business_address: businessInfo.businessAddress,
      business_description: businessInfo.businessDescription,
      website: businessInfo.website,
      tax_id: businessInfo.taxId
    }

    const response = await api.post("/api/v1/merchants/", merchantData)
    return response.data
  },

  /**
   * Link current user to merchant account
   */
  async linkUserToMerchant(businessInfo: BusinessInfo): Promise<MerchantResponse> {
    const merchantData: OnboardingMerchantRequest = {
      business_name: businessInfo.businessName,
      owner_name: businessInfo.ownerName,
      email: businessInfo.email,
      phone: businessInfo.phone,
      business_type: businessInfo.businessType.toUpperCase(),
      business_address: businessInfo.businessAddress,
      business_description: businessInfo.businessDescription,
      website: businessInfo.website,
      tax_id: businessInfo.taxId
    }

    const response = await api.post("/api/v1/merchants/link-user-merchant", merchantData)
    return response.data
  },

  /**
   * Create M-Pesa channel for merchant
   */
  async createMpesaChannel(
    merchantId: number, 
    channelData: MpesaChannelData
  ): Promise<any> {
    const requestData: OnboardingMpesaChannelRequest = {
      name: channelData.name,
      shortcode: channelData.shortcode,
      channel_type: channelData.channel_type,
      environment: channelData.environment,
      consumer_key: channelData.consumer_key,
      consumer_secret: channelData.consumer_secret,
      passkey: channelData.passkey,
      validation_url: channelData.validation_url,
      confirmation_url: channelData.confirmation_url,
      callback_url: channelData.callback_url,
      account_mapping: channelData.account_mapping,
      is_primary: channelData.is_primary
    }

    // Use the new M-Pesa channels API
    const response = await api.post("/api/v1/mpesa/channels", {
      merchant_id: merchantId,
      ...requestData
    })
    return response.data
  },

  /**
   * Create multiple M-Pesa channels
   */
  async createMpesaChannels(
    merchantId: number, 
    channels: MpesaChannelData[]
  ): Promise<any[]> {
    const results = []
    
    for (const channel of channels) {
      try {
        const result = await this.createMpesaChannel(merchantId, channel)
        results.push(result)
      } catch (error) {
        console.error(`Failed to create channel ${channel.name}:`, error)
        throw new Error(`Failed to create M-Pesa channel: ${channel.name}`)
      }
    }
    
    return results
  },

  /**
   * Verify M-Pesa channel credentials
   */
  async verifyMpesaChannel(
    merchantId: number, 
    channelId: number
  ): Promise<ChannelVerificationResult> {
    try {
      const response = await api.post(
        `/api/v1/merchants/${merchantId}/mpesa/channels/${channelId}/verify`
      )
      
      return {
        channel_id: channelId,
        verified: response.data.verified || false,
        status: response.data.status || "unknown",
        verification_details: response.data
      }
    } catch (error: any) {
      return {
        channel_id: channelId,
        verified: false,
        status: "error",
        error: error.response?.data?.detail || error.message
      }
    }
  },

  /**
   * Verify all M-Pesa channels
   */
  async verifyAllChannels(
    merchantId: number, 
    channels: any[]
  ): Promise<ChannelVerificationResult[]> {
    const results = []
    
    for (const channel of channels) {
      const result = await this.verifyMpesaChannel(merchantId, channel.id)
      results.push(result)
    }
    
    return results
  },

  /**
   * Register URLs for M-Pesa channel
   */
  async registerChannelUrls(
    merchantId: number,
    channelId: number,
    urls: {
      validation_url: string
      confirmation_url: string
      response_type?: string
    }
  ): Promise<any> {
    const response = await api.post(
      `/api/v1/merchants/${merchantId}/mpesa/channels/${channelId}/register-urls`,
      urls
    )
    return response.data
  },

  /**
   * Create loyalty program
   */
  async createLoyaltyProgram(
    merchantId: number, 
    loyaltyConfig: LoyaltyProgramConfig
  ): Promise<LoyaltyProgramResponse> {
    const programData: OnboardingLoyaltyProgramRequest = {
      name: loyaltyConfig.name,
      description: loyaltyConfig.description,
      points_per_shilling: loyaltyConfig.points_per_shilling,
      redemption_rate: loyaltyConfig.redemption_rate,
      tier_system_enabled: loyaltyConfig.tier_system_enabled,
      tiers: loyaltyConfig.tiers,
      welcome_bonus: loyaltyConfig.welcome_bonus,
      referral_bonus: loyaltyConfig.referral_bonus,
      birthday_bonus: loyaltyConfig.birthday_bonus,
      merchant_id: merchantId
    }

    const response = await api.post("/api/v1/loyalty-programs/", programData)
    return response.data
  },

  /**
   * Complete onboarding process
   */
  async completeOnboarding(
    businessInfo: BusinessInfo,
    mpesaChannels: MpesaChannelData[],
    loyaltyProgram: LoyaltyProgramConfig,
    linkToUser: boolean = true
  ): Promise<OnboardingResult> {
    try {
      // Step 1: Create or link merchant
      const merchant = linkToUser 
        ? await this.linkUserToMerchant(businessInfo)
        : await this.createMerchant(businessInfo)

      // Step 2: Create M-Pesa channels
      const channels = await this.createMpesaChannels(merchant.id, mpesaChannels)

      // Step 3: Verify channels (in background, don't block)
      const verificationResults = await this.verifyAllChannels(merchant.id, channels)

      // Step 4: Create loyalty program
      const loyaltyProgramResponse = await this.createLoyaltyProgram(merchant.id, loyaltyProgram)

      // Step 5: Register URLs for channels that have them
      for (const [index, channel] of channels.entries()) {
        const originalChannel = mpesaChannels[index]
        if (originalChannel.validation_url || originalChannel.confirmation_url) {
          try {
            await this.registerChannelUrls(merchant.id, channel.id, {
              validation_url: originalChannel.validation_url || "",
              confirmation_url: originalChannel.confirmation_url || "",
              response_type: "Completed"
            })
          } catch (error) {
            console.warn(`Failed to register URLs for channel ${channel.id}:`, error)
          }
        }
      }

      return {
        merchant,
        channels,
        loyalty_program: loyaltyProgramResponse,
        verification_results: verificationResults
      }
    } catch (error) {
      console.error("Onboarding failed:", error)
      throw error
    }
  },

  /**
   * Test M-Pesa channel with simulation
   */
  async testMpesaChannel(
    merchantId: number,
    channelId: number,
    testData: {
      amount: number
      customer_phone: string
      bill_ref?: string
    }
  ): Promise<any> {
    const response = await api.post(
      `/api/v1/merchants/${merchantId}/mpesa/channels/${channelId}/simulate`,
      testData
    )
    return response.data
  },

  /**
   * Get onboarding status for user
   */
  async getOnboardingStatus(): Promise<{
    completed: boolean
    merchant_id?: number
    current_step?: string
    progress_percentage?: number
  }> {
    try {
      const response = await api.get("/api/v1/auth/onboarding-status")
      return response.data
    } catch (error) {
      return {
        completed: false,
        current_step: "business-info",
        progress_percentage: 0
      }
    }
  },

  /**
   * Update onboarding progress
   */
  async updateOnboardingProgress(
    step: string,
    completed: boolean,
    data?: any
  ): Promise<void> {
    await api.post("/api/v1/auth/onboarding-progress", {
      step,
      completed,
      data
    })
  },

  /**
   * Mark onboarding as completed
   */
  async markOnboardingCompleted(): Promise<void> {
    await api.post("/api/v1/auth/complete-onboarding")
  }
}
