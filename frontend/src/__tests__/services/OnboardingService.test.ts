/**
 * @jest-environment jsdom
 */

import { jest } from '@jest/globals'
import { onboardingService } from '@/services/onboarding-service'
import type { BusinessInfo, MpesaChannelData, LoyaltyProgramConfig } from '@/contexts/onboarding-context'

// Mock the API module
const mockApi = {
  post: jest.fn(),
  get: jest.fn(),
  put: jest.fn(),
  delete: jest.fn()
}

jest.mock('@/lib/api', () => ({
  default: mockApi
}))

describe('OnboardingService', () => {
  beforeEach(() => {
    jest.clearAllMocks()
  })

  const mockBusinessInfo: BusinessInfo = {
    businessName: "Test Electronics Store",
    ownerName: "John Doe",
    email: "john@teststore.com",
    phone: "254712345678",
    businessType: "retail",
    businessAddress: "123 Test Street, Nairobi",
    businessDescription: "Electronics and gadgets store",
    website: "https://teststore.com",
    taxId: "P051234567M"
  }

  const mockMpesaChannel: MpesaChannelData = {
    name: "Main PayBill",
    shortcode: "174379",
    channel_type: "paybill",
    environment: "sandbox",
    consumer_key: "test_consumer_key",
    consumer_secret: "test_consumer_secret",
    passkey: "test_passkey",
    validation_url: "https://teststore.com/mpesa/validate",
    confirmation_url: "https://teststore.com/mpesa/confirm",
    account_mapping: {
      "default": "standard_loyalty",
      "VIP*": "vip_program"
    },
    is_primary: true
  }

  const mockLoyaltyProgram: LoyaltyProgramConfig = {
    name: "VIP Rewards",
    description: "Earn points with every purchase",
    points_per_shilling: 1,
    redemption_rate: 100,
    tier_system_enabled: true,
    tiers: [
      {
        name: "Bronze",
        min_points: 0,
        multiplier: 1,
        benefits: ["Standard rewards"]
      },
      {
        name: "Silver",
        min_points: 1000,
        multiplier: 1.2,
        benefits: ["20% bonus points", "Priority support"]
      }
    ],
    welcome_bonus: 100,
    referral_bonus: 200,
    birthday_bonus: 500
  }

  describe('Merchant Creation', () => {
    it('creates merchant successfully', async () => {
      const mockMerchantResponse = {
        id: 123,
        business_name: "Test Electronics Store",
        owner_name: "John Doe",
        email: "john@teststore.com",
        phone: "254712345678",
        business_type: "RETAIL",
        status: "active"
      }

      mockApi.post.mockResolvedValue({ data: mockMerchantResponse })

      const result = await onboardingService.createMerchant(mockBusinessInfo)

      expect(mockApi.post).toHaveBeenCalledWith("/api/v1/merchants/", {
        business_name: "Test Electronics Store",
        owner_name: "John Doe",
        email: "john@teststore.com",
        phone: "254712345678",
        business_type: "RETAIL",
        business_address: "123 Test Street, Nairobi",
        business_description: "Electronics and gadgets store",
        website: "https://teststore.com",
        tax_id: "P051234567M"
      })

      expect(result).toEqual(mockMerchantResponse)
    })

    it('links user to merchant successfully', async () => {
      const mockMerchantResponse = {
        id: 123,
        business_name: "Test Electronics Store",
        owner_name: "John Doe",
        email: "john@teststore.com"
      }

      mockApi.post.mockResolvedValue({ data: mockMerchantResponse })

      const result = await onboardingService.linkUserToMerchant(mockBusinessInfo)

      expect(mockApi.post).toHaveBeenCalledWith("/api/v1/merchants/link-user-merchant", expect.objectContaining({
        business_name: "Test Electronics Store",
        owner_name: "John Doe",
        email: "john@teststore.com",
        phone: "254712345678",
        business_type: "RETAIL"
      }))

      expect(result).toEqual(mockMerchantResponse)
    })

    it('handles merchant creation errors', async () => {
      const mockError = new Error('Merchant creation failed')
      mockApi.post.mockRejectedValue(mockError)

      await expect(onboardingService.createMerchant(mockBusinessInfo))
        .rejects.toThrow('Merchant creation failed')
    })
  })

  describe('M-Pesa Channel Management', () => {
    it('creates M-Pesa channel successfully', async () => {
      const mockChannelResponse = {
        id: 456,
        merchant_id: 123,
        name: "Main PayBill",
        shortcode: "174379",
        channel_type: "paybill",
        environment: "sandbox",
        status: "configured",
        is_primary: true
      }

      mockApi.post.mockResolvedValue({ data: mockChannelResponse })

      const result = await onboardingService.createMpesaChannel(123, mockMpesaChannel)

      expect(mockApi.post).toHaveBeenCalledWith("/api/v1/mpesa/channels", {
        merchant_id: 123,
        name: "Main PayBill",
        shortcode: "174379",
        channel_type: "paybill",
        environment: "sandbox",
        consumer_key: "test_consumer_key",
        consumer_secret: "test_consumer_secret",
        passkey: "test_passkey",
        validation_url: "https://teststore.com/mpesa/validate",
        confirmation_url: "https://teststore.com/mpesa/confirm",
        callback_url: undefined,
        account_mapping: {
          "default": "standard_loyalty",
          "VIP*": "vip_program"
        },
        is_primary: true
      })

      expect(result).toEqual(mockChannelResponse)
    })

    it('creates multiple M-Pesa channels successfully', async () => {
      const channels = [
        mockMpesaChannel,
        {
          ...mockMpesaChannel,
          name: "Shop Till",
          shortcode: "123456",
          channel_type: "till" as const,
          is_primary: false
        }
      ]

      const mockResponses = [
        { id: 456, name: "Main PayBill" },
        { id: 789, name: "Shop Till" }
      ]

      mockApi.post
        .mockResolvedValueOnce({ data: mockResponses[0] })
        .mockResolvedValueOnce({ data: mockResponses[1] })

      const results = await onboardingService.createMpesaChannels(123, channels)

      expect(mockApi.post).toHaveBeenCalledTimes(2)
      expect(results).toHaveLength(2)
      expect(results[0]).toEqual(mockResponses[0])
      expect(results[1]).toEqual(mockResponses[1])
    })

    it('handles channel creation failure in batch', async () => {
      const channels = [mockMpesaChannel, { ...mockMpesaChannel, name: "Second Channel" }]

      mockApi.post
        .mockResolvedValueOnce({ data: { id: 456 } })
        .mockRejectedValueOnce(new Error('Channel creation failed'))

      await expect(onboardingService.createMpesaChannels(123, channels))
        .rejects.toThrow('Failed to create M-Pesa channel: Second Channel')
    })

    it('verifies M-Pesa channel successfully', async () => {
      const mockVerificationResponse = {
        verified: true,
        status: "verified",
        verification_details: {
          shortcode: "174379",
          response_code: "0"
        }
      }

      mockApi.post.mockResolvedValue({ data: mockVerificationResponse })

      const result = await onboardingService.verifyMpesaChannel(123, 456)

      expect(mockApi.post).toHaveBeenCalledWith(
        "/api/v1/merchants/123/mpesa/channels/456/verify"
      )

      expect(result).toEqual({
        channel_id: 456,
        verified: true,
        status: "verified",
        verification_details: mockVerificationResponse
      })
    })

    it('handles channel verification failure', async () => {
      const mockError = {
        response: {
          data: {
            detail: "Invalid credentials"
          }
        }
      }

      mockApi.post.mockRejectedValue(mockError)

      const result = await onboardingService.verifyMpesaChannel(123, 456)

      expect(result).toEqual({
        channel_id: 456,
        verified: false,
        status: "error",
        error: "Invalid credentials"
      })
    })

    it('verifies all channels', async () => {
      const channels = [
        { id: 456, name: "Channel 1" },
        { id: 789, name: "Channel 2" }
      ]

      mockApi.post
        .mockResolvedValueOnce({ data: { verified: true, status: "verified" } })
        .mockResolvedValueOnce({ data: { verified: false, status: "failed" } })

      const results = await onboardingService.verifyAllChannels(123, channels)

      expect(results).toHaveLength(2)
      expect(results[0].verified).toBe(true)
      expect(results[1].verified).toBe(false)
    })

    it('registers channel URLs successfully', async () => {
      const mockResponse = {
        registered: true,
        ResponseCode: "0"
      }

      mockApi.post.mockResolvedValue({ data: mockResponse })

      const urls = {
        validation_url: "https://test.com/validate",
        confirmation_url: "https://test.com/confirm",
        response_type: "Completed"
      }

      const result = await onboardingService.registerChannelUrls(123, 456, urls)

      expect(mockApi.post).toHaveBeenCalledWith(
        "/api/v1/merchants/123/mpesa/channels/456/register-urls",
        urls
      )

      expect(result).toEqual(mockResponse)
    })
  })

  describe('Loyalty Program Management', () => {
    it('creates loyalty program successfully', async () => {
      const mockLoyaltyResponse = {
        id: 789,
        merchant_id: 123,
        name: "VIP Rewards",
        description: "Earn points with every purchase",
        points_per_shilling: 1,
        redemption_rate: 100,
        tier_system_enabled: true,
        status: "active"
      }

      mockApi.post.mockResolvedValue({ data: mockLoyaltyResponse })

      const result = await onboardingService.createLoyaltyProgram(123, mockLoyaltyProgram)

      expect(mockApi.post).toHaveBeenCalledWith("/api/v1/loyalty-programs/", {
        name: "VIP Rewards",
        description: "Earn points with every purchase",
        points_per_shilling: 1,
        redemption_rate: 100,
        tier_system_enabled: true,
        tiers: mockLoyaltyProgram.tiers,
        welcome_bonus: 100,
        referral_bonus: 200,
        birthday_bonus: 500,
        merchant_id: 123
      })

      expect(result).toEqual(mockLoyaltyResponse)
    })

    it('handles loyalty program creation errors', async () => {
      const mockError = new Error('Loyalty program creation failed')
      mockApi.post.mockRejectedValue(mockError)

      await expect(onboardingService.createLoyaltyProgram(123, mockLoyaltyProgram))
        .rejects.toThrow('Loyalty program creation failed')
    })
  })

  describe('Complete Onboarding Flow', () => {
    it('completes onboarding successfully with user linking', async () => {
      const mockMerchantResponse = { id: 123, business_name: "Test Store" }
      const mockChannelResponse = { id: 456, name: "Test Channel" }
      const mockLoyaltyResponse = { id: 789, name: "VIP Rewards" }
      const mockVerificationResponse = { channel_id: 456, verified: true }

      // Mock API responses
      mockApi.post
        .mockResolvedValueOnce({ data: mockMerchantResponse }) // linkUserToMerchant
        .mockResolvedValueOnce({ data: mockChannelResponse }) // createMpesaChannel
        .mockResolvedValueOnce({ data: mockVerificationResponse }) // verifyMpesaChannel
        .mockResolvedValueOnce({ data: mockLoyaltyResponse }) // createLoyaltyProgram

      const result = await onboardingService.completeOnboarding(
        mockBusinessInfo,
        [mockMpesaChannel],
        mockLoyaltyProgram,
        true // linkToUser
      )

      expect(result).toEqual({
        merchant: mockMerchantResponse,
        channels: [mockChannelResponse],
        loyalty_program: mockLoyaltyResponse,
        verification_results: [mockVerificationResponse]
      })

      // Verify correct API calls were made
      expect(mockApi.post).toHaveBeenCalledWith("/api/v1/merchants/link-user-merchant", expect.any(Object))
      expect(mockApi.post).toHaveBeenCalledWith("/api/v1/mpesa/channels", expect.any(Object))
      expect(mockApi.post).toHaveBeenCalledWith("/api/v1/loyalty-programs/", expect.any(Object))
    })

    it('completes onboarding without user linking', async () => {
      const mockMerchantResponse = { id: 123, business_name: "Test Store" }
      const mockChannelResponse = { id: 456, name: "Test Channel" }
      const mockLoyaltyResponse = { id: 789, name: "VIP Rewards" }

      mockApi.post
        .mockResolvedValueOnce({ data: mockMerchantResponse }) // createMerchant
        .mockResolvedValueOnce({ data: mockChannelResponse }) // createMpesaChannel
        .mockResolvedValueOnce({ data: { verified: true } }) // verifyMpesaChannel
        .mockResolvedValueOnce({ data: mockLoyaltyResponse }) // createLoyaltyProgram

      const result = await onboardingService.completeOnboarding(
        mockBusinessInfo,
        [mockMpesaChannel],
        mockLoyaltyProgram,
        false // linkToUser
      )

      expect(mockApi.post).toHaveBeenCalledWith("/api/v1/merchants/", expect.any(Object))
      expect(result.merchant).toEqual(mockMerchantResponse)
    })

    it('registers URLs for channels that have them', async () => {
      const channelWithUrls = {
        ...mockMpesaChannel,
        validation_url: "https://test.com/validate",
        confirmation_url: "https://test.com/confirm"
      }

      const mockMerchantResponse = { id: 123 }
      const mockChannelResponse = { id: 456 }
      const mockLoyaltyResponse = { id: 789 }

      mockApi.post
        .mockResolvedValueOnce({ data: mockMerchantResponse })
        .mockResolvedValueOnce({ data: mockChannelResponse })
        .mockResolvedValueOnce({ data: { verified: true } })
        .mockResolvedValueOnce({ data: mockLoyaltyResponse })
        .mockResolvedValueOnce({ data: { registered: true } }) // registerChannelUrls

      await onboardingService.completeOnboarding(
        mockBusinessInfo,
        [channelWithUrls],
        mockLoyaltyProgram,
        true
      )

      // Should call URL registration
      expect(mockApi.post).toHaveBeenCalledWith(
        "/api/v1/merchants/123/mpesa/channels/456/register-urls",
        {
          validation_url: "https://test.com/validate",
          confirmation_url: "https://test.com/confirm",
          response_type: "Completed"
        }
      )
    })

    it('handles onboarding failure gracefully', async () => {
      mockApi.post.mockRejectedValue(new Error('Merchant creation failed'))

      await expect(onboardingService.completeOnboarding(
        mockBusinessInfo,
        [mockMpesaChannel],
        mockLoyaltyProgram
      )).rejects.toThrow('Merchant creation failed')
    })

    it('continues onboarding even if URL registration fails', async () => {
      const channelWithUrls = {
        ...mockMpesaChannel,
        validation_url: "https://test.com/validate",
        confirmation_url: "https://test.com/confirm"
      }

      const mockMerchantResponse = { id: 123 }
      const mockChannelResponse = { id: 456 }
      const mockLoyaltyResponse = { id: 789 }

      mockApi.post
        .mockResolvedValueOnce({ data: mockMerchantResponse })
        .mockResolvedValueOnce({ data: mockChannelResponse })
        .mockResolvedValueOnce({ data: { verified: true } })
        .mockResolvedValueOnce({ data: mockLoyaltyResponse })
        .mockRejectedValueOnce(new Error('URL registration failed')) // registerChannelUrls fails

      // Should not throw error, just log warning
      const result = await onboardingService.completeOnboarding(
        mockBusinessInfo,
        [channelWithUrls],
        mockLoyaltyProgram,
        true
      )

      expect(result.merchant).toEqual(mockMerchantResponse)
      expect(result.channels).toEqual([mockChannelResponse])
      expect(result.loyalty_program).toEqual(mockLoyaltyResponse)
    })
  })

  describe('Testing and Utilities', () => {
    it('tests M-Pesa channel successfully', async () => {
      const mockTestResponse = {
        status: "success",
        conversation_id: "AG_20240115_12345",
        amount: "100.0",
        customer_phone: "254712345678"
      }

      mockApi.post.mockResolvedValue({ data: mockTestResponse })

      const testData = {
        amount: 100,
        customer_phone: "254712345678",
        bill_ref: "TEST001"
      }

      const result = await onboardingService.testMpesaChannel(123, 456, testData)

      expect(mockApi.post).toHaveBeenCalledWith(
        "/api/v1/merchants/123/mpesa/channels/456/simulate",
        testData
      )

      expect(result).toEqual(mockTestResponse)
    })

    it('gets onboarding status successfully', async () => {
      const mockStatusResponse = {
        completed: false,
        merchant_id: 123,
        current_step: "mpesa-setup",
        progress_percentage: 50
      }

      mockApi.get.mockResolvedValue({ data: mockStatusResponse })

      const result = await onboardingService.getOnboardingStatus()

      expect(mockApi.get).toHaveBeenCalledWith("/api/v1/auth/onboarding-status")
      expect(result).toEqual(mockStatusResponse)
    })

    it('handles onboarding status error gracefully', async () => {
      mockApi.get.mockRejectedValue(new Error('Status fetch failed'))

      const result = await onboardingService.getOnboardingStatus()

      expect(result).toEqual({
        completed: false,
        current_step: "business-info",
        progress_percentage: 0
      })
    })

    it('updates onboarding progress successfully', async () => {
      mockApi.post.mockResolvedValue({ data: { success: true } })

      await onboardingService.updateOnboardingProgress("business-info", true, { test: "data" })

      expect(mockApi.post).toHaveBeenCalledWith("/api/v1/auth/onboarding-progress", {
        step: "business-info",
        completed: true,
        data: { test: "data" }
      })
    })

    it('marks onboarding as completed successfully', async () => {
      mockApi.post.mockResolvedValue({ data: { success: true } })

      await onboardingService.markOnboardingCompleted()

      expect(mockApi.post).toHaveBeenCalledWith("/api/v1/auth/complete-onboarding")
    })
  })

  describe('Error Handling and Edge Cases', () => {
    it('handles network errors', async () => {
      const networkError = new Error('Network Error')
      mockApi.post.mockRejectedValue(networkError)

      await expect(onboardingService.createMerchant(mockBusinessInfo))
        .rejects.toThrow('Network Error')
    })

    it('handles API validation errors', async () => {
      const validationError = {
        response: {
          status: 400,
          data: {
            detail: "Invalid business type"
          }
        }
      }

      mockApi.post.mockRejectedValue(validationError)

      await expect(onboardingService.createMerchant(mockBusinessInfo))
        .rejects.toMatchObject(validationError)
    })

    it('handles authentication errors', async () => {
      const authError = {
        response: {
          status: 401,
          data: {
            detail: "Not authenticated"
          }
        }
      }

      mockApi.post.mockRejectedValue(authError)

      await expect(onboardingService.linkUserToMerchant(mockBusinessInfo))
        .rejects.toMatchObject(authError)
    })

    it('handles server errors', async () => {
      const serverError = {
        response: {
          status: 500,
          data: {
            detail: "Internal server error"
          }
        }
      }

      mockApi.post.mockRejectedValue(serverError)

      await expect(onboardingService.createLoyaltyProgram(123, mockLoyaltyProgram))
        .rejects.toMatchObject(serverError)
    })
  })
})
