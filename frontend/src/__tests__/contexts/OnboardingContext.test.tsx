/**
 * @jest-environment jsdom
 */

import React from 'react'
import { renderHook, act } from '@testing-library/react'
import { jest } from '@jest/globals'

// Mock toast
jest.mock('react-hot-toast', () => ({
  toast: {
    success: jest.fn(),
    error: jest.fn(),
    loading: jest.fn()
  }
}))

import { OnboardingProvider, useOnboarding, type MpesaChannelData } from '@/contexts/onboarding-context'

const wrapper = ({ children }: { children: React.ReactNode }) => (
  <OnboardingProvider>{children}</OnboardingProvider>
)

describe('OnboardingContext', () => {
  describe('Business Info Management', () => {
    it('initializes with default business info', () => {
      const { result } = renderHook(() => useOnboarding(), { wrapper })

      expect(result.current.data.businessInfo).toEqual({
        businessName: "",
        ownerName: "",
        email: "",
        phone: "",
        businessType: "",
        businessAddress: "",
        businessDescription: "",
        website: "",
        taxId: ""
      })
    })

    it('updates business info correctly', () => {
      const { result } = renderHook(() => useOnboarding(), { wrapper })

      act(() => {
        result.current.updateBusinessInfo({
          businessName: "Test Store",
          ownerName: "John Doe",
          email: "john@test.com"
        })
      })

      expect(result.current.data.businessInfo.businessName).toBe("Test Store")
      expect(result.current.data.businessInfo.ownerName).toBe("John Doe")
      expect(result.current.data.businessInfo.email).toBe("john@test.com")
      // Other fields should remain unchanged
      expect(result.current.data.businessInfo.phone).toBe("")
    })

    it('validates business info correctly', () => {
      const { result } = renderHook(() => useOnboarding(), { wrapper })

      // Should fail validation with empty data
      expect(result.current.validateBusinessInfo()).toBe(false)

      // Fill in valid data
      act(() => {
        result.current.updateBusinessInfo({
          businessName: "Test Store",
          ownerName: "John Doe",
          email: "john@test.com",
          phone: "254712345678",
          businessType: "retail"
        })
      })

      expect(result.current.validateBusinessInfo()).toBe(true)
    })

    it('validates email format', () => {
      const { result } = renderHook(() => useOnboarding(), { wrapper })

      act(() => {
        result.current.updateBusinessInfo({
          businessName: "Test Store",
          ownerName: "John Doe",
          email: "invalid-email",
          phone: "254712345678",
          businessType: "retail"
        })
      })

      expect(result.current.validateBusinessInfo()).toBe(false)
    })

    it('validates phone number format', () => {
      const { result } = renderHook(() => useOnboarding(), { wrapper })

      act(() => {
        result.current.updateBusinessInfo({
          businessName: "Test Store",
          ownerName: "John Doe",
          email: "john@test.com",
          phone: "123456789", // Invalid format
          businessType: "retail"
        })
      })

      expect(result.current.validateBusinessInfo()).toBe(false)

      // Test valid phone number
      act(() => {
        result.current.updateBusinessInfo({
          phone: "254712345678"
        })
      })

      expect(result.current.validateBusinessInfo()).toBe(true)
    })
  })

  describe('M-Pesa Channel Management', () => {
    const validChannel: MpesaChannelData = {
      name: "Test Channel",
      shortcode: "174379",
      channel_type: "paybill",
      environment: "sandbox",
      consumer_key: "test_key",
      consumer_secret: "test_secret",
      is_primary: true
    }

    it('initializes with empty channels array', () => {
      const { result } = renderHook(() => useOnboarding(), { wrapper })

      expect(result.current.data.mpesaChannels).toEqual([])
    })

    it('adds M-Pesa channel correctly', () => {
      const { result } = renderHook(() => useOnboarding(), { wrapper })

      act(() => {
        result.current.addMpesaChannel(validChannel)
      })

      expect(result.current.data.mpesaChannels).toHaveLength(1)
      expect(result.current.data.mpesaChannels[0]).toEqual(validChannel)
    })

    it('updates M-Pesa channel correctly', () => {
      const { result } = renderHook(() => useOnboarding(), { wrapper })

      act(() => {
        result.current.addMpesaChannel(validChannel)
      })

      act(() => {
        result.current.updateMpesaChannel(0, { name: "Updated Channel" })
      })

      expect(result.current.data.mpesaChannels[0].name).toBe("Updated Channel")
      expect(result.current.data.mpesaChannels[0].shortcode).toBe("174379") // Should remain unchanged
    })

    it('removes M-Pesa channel correctly', () => {
      const { result } = renderHook(() => useOnboarding(), { wrapper })

      act(() => {
        result.current.addMpesaChannel(validChannel)
        result.current.addMpesaChannel({
          ...validChannel,
          name: "Second Channel",
          shortcode: "123456",
          is_primary: false
        })
      })

      expect(result.current.data.mpesaChannels).toHaveLength(2)

      act(() => {
        result.current.removeMpesaChannel(0)
      })

      expect(result.current.data.mpesaChannels).toHaveLength(1)
      expect(result.current.data.mpesaChannels[0].name).toBe("Second Channel")
    })

    it('validates M-Pesa channels correctly', () => {
      const { result } = renderHook(() => useOnboarding(), { wrapper })

      // Should fail with no channels
      expect(result.current.validateMpesaChannels()).toBe(false)

      // Add valid channel
      act(() => {
        result.current.addMpesaChannel(validChannel)
      })

      expect(result.current.validateMpesaChannels()).toBe(true)
    })

    it('validates channel required fields', () => {
      const { result } = renderHook(() => useOnboarding(), { wrapper })

      const invalidChannel = {
        ...validChannel,
        name: "", // Missing name
      }

      act(() => {
        result.current.addMpesaChannel(invalidChannel)
      })

      expect(result.current.validateMpesaChannels()).toBe(false)
    })

    it('validates shortcode format for different channel types', () => {
      const { result } = renderHook(() => useOnboarding(), { wrapper })

      const invalidShortcodeChannel = {
        ...validChannel,
        shortcode: "123", // Too short
      }

      act(() => {
        result.current.addMpesaChannel(invalidShortcodeChannel)
      })

      expect(result.current.validateMpesaChannels()).toBe(false)
    })

    it('validates URL formats', () => {
      const { result } = renderHook(() => useOnboarding(), { wrapper })

      const invalidUrlChannel = {
        ...validChannel,
        validation_url: "invalid-url",
      }

      act(() => {
        result.current.addMpesaChannel(invalidUrlChannel)
      })

      expect(result.current.validateMpesaChannels()).toBe(false)
    })

    it('ensures only one primary channel', () => {
      const { result } = renderHook(() => useOnboarding(), { wrapper })

      act(() => {
        result.current.addMpesaChannel(validChannel)
        result.current.addMpesaChannel({
          ...validChannel,
          name: "Second Channel",
          shortcode: "123456",
          is_primary: true // Both channels are primary
        })
      })

      expect(result.current.validateMpesaChannels()).toBe(false)
    })

    it('requires at least one primary channel', () => {
      const { result } = renderHook(() => useOnboarding(), { wrapper })

      act(() => {
        result.current.addMpesaChannel({
          ...validChannel,
          is_primary: false // No primary channel
        })
      })

      expect(result.current.validateMpesaChannels()).toBe(false)
    })
  })

  describe('Loyalty Program Management', () => {
    it('initializes with default loyalty program', () => {
      const { result } = renderHook(() => useOnboarding(), { wrapper })

      expect(result.current.data.loyaltyProgram.name).toBe("Loyalty Rewards")
      expect(result.current.data.loyaltyProgram.points_per_shilling).toBe(1)
      expect(result.current.data.loyaltyProgram.redemption_rate).toBe(100)
      expect(result.current.data.loyaltyProgram.tier_system_enabled).toBe(true)
      expect(result.current.data.loyaltyProgram.tiers).toHaveLength(4)
    })

    it('updates loyalty program correctly', () => {
      const { result } = renderHook(() => useOnboarding(), { wrapper })

      act(() => {
        result.current.updateLoyaltyProgram({
          name: "VIP Rewards",
          points_per_shilling: 2,
          redemption_rate: 50
        })
      })

      expect(result.current.data.loyaltyProgram.name).toBe("VIP Rewards")
      expect(result.current.data.loyaltyProgram.points_per_shilling).toBe(2)
      expect(result.current.data.loyaltyProgram.redemption_rate).toBe(50)
      // Other fields should remain unchanged
      expect(result.current.data.loyaltyProgram.tier_system_enabled).toBe(true)
    })

    it('validates loyalty program correctly', () => {
      const { result } = renderHook(() => useOnboarding(), { wrapper })

      // Should pass with default values
      expect(result.current.validateLoyaltyProgram()).toBe(true)

      // Test with invalid values
      act(() => {
        result.current.updateLoyaltyProgram({
          name: "", // Empty name
        })
      })

      expect(result.current.validateLoyaltyProgram()).toBe(false)
    })

    it('validates points per shilling', () => {
      const { result } = renderHook(() => useOnboarding(), { wrapper })

      act(() => {
        result.current.updateLoyaltyProgram({
          points_per_shilling: 0 // Invalid
        })
      })

      expect(result.current.validateLoyaltyProgram()).toBe(false)

      act(() => {
        result.current.updateLoyaltyProgram({
          points_per_shilling: -1 // Invalid
        })
      })

      expect(result.current.validateLoyaltyProgram()).toBe(false)
    })

    it('validates redemption rate', () => {
      const { result } = renderHook(() => useOnboarding(), { wrapper })

      act(() => {
        result.current.updateLoyaltyProgram({
          redemption_rate: 0 // Invalid
        })
      })

      expect(result.current.validateLoyaltyProgram()).toBe(false)
    })

    it('validates tier configuration when enabled', () => {
      const { result } = renderHook(() => useOnboarding(), { wrapper })

      act(() => {
        result.current.updateLoyaltyProgram({
          tier_system_enabled: true,
          tiers: [
            {
              name: "", // Invalid empty name
              min_points: 0,
              multiplier: 1,
              benefits: ["Standard rewards"]
            }
          ]
        })
      })

      expect(result.current.validateLoyaltyProgram()).toBe(false)
    })

    it('validates tier minimum points', () => {
      const { result } = renderHook(() => useOnboarding(), { wrapper })

      act(() => {
        result.current.updateLoyaltyProgram({
          tiers: [
            {
              name: "Bronze",
              min_points: -100, // Invalid negative
              multiplier: 1,
              benefits: ["Standard rewards"]
            }
          ]
        })
      })

      expect(result.current.validateLoyaltyProgram()).toBe(false)
    })

    it('validates tier multiplier', () => {
      const { result } = renderHook(() => useOnboarding(), { wrapper })

      act(() => {
        result.current.updateLoyaltyProgram({
          tiers: [
            {
              name: "Bronze",
              min_points: 0,
              multiplier: 0, // Invalid
              benefits: ["Standard rewards"]
            }
          ]
        })
      })

      expect(result.current.validateLoyaltyProgram()).toBe(false)
    })

    it('validates tier ordering by min_points', () => {
      const { result } = renderHook(() => useOnboarding(), { wrapper })

      act(() => {
        result.current.updateLoyaltyProgram({
          tiers: [
            {
              name: "Gold",
              min_points: 1000, // Should be after Bronze
              multiplier: 1.5,
              benefits: ["Gold rewards"]
            },
            {
              name: "Bronze",
              min_points: 0,
              multiplier: 1,
              benefits: ["Standard rewards"]
            }
          ]
        })
      })

      expect(result.current.validateLoyaltyProgram()).toBe(false)
    })
  })

  describe('Utility Functions', () => {
    it('sets merchant ID correctly', () => {
      const { result } = renderHook(() => useOnboarding(), { wrapper })

      act(() => {
        result.current.setMerchantId(123)
      })

      expect(result.current.data.currentMerchantId).toBe(123)
    })

    it('resets onboarding data correctly', () => {
      const { result } = renderHook(() => useOnboarding(), { wrapper })

      // Modify some data
      act(() => {
        result.current.updateBusinessInfo({ businessName: "Test Store" })
        result.current.addMpesaChannel({
          name: "Test Channel",
          shortcode: "174379",
          channel_type: "paybill",
          environment: "sandbox",
          consumer_key: "test_key",
          consumer_secret: "test_secret",
          is_primary: true
        })
        result.current.setMerchantId(123)
      })

      // Reset
      act(() => {
        result.current.resetOnboarding()
      })

      expect(result.current.data.businessInfo.businessName).toBe("")
      expect(result.current.data.mpesaChannels).toHaveLength(0)
      expect(result.current.data.currentMerchantId).toBeUndefined()
      expect(result.current.data.loyaltyProgram.name).toBe("Loyalty Rewards") // Back to default
    })
  })

  describe('Error Handling', () => {
    it('throws error when used outside provider', () => {
      expect(() => {
        renderHook(() => useOnboarding())
      }).toThrow('useOnboarding must be used within an OnboardingProvider')
    })
  })

  describe('Integration Scenarios', () => {
    it('handles complete onboarding flow', () => {
      const { result } = renderHook(() => useOnboarding(), { wrapper })

      // Step 1: Business Info
      act(() => {
        result.current.updateBusinessInfo({
          businessName: "Complete Test Store",
          ownerName: "Jane Doe",
          email: "jane@test.com",
          phone: "254712345678",
          businessType: "retail"
        })
      })

      expect(result.current.validateBusinessInfo()).toBe(true)

      // Step 2: M-Pesa Channels
      act(() => {
        result.current.addMpesaChannel({
          name: "Main PayBill",
          shortcode: "174379",
          channel_type: "paybill",
          environment: "sandbox",
          consumer_key: "test_key",
          consumer_secret: "test_secret",
          is_primary: true
        })
      })

      expect(result.current.validateMpesaChannels()).toBe(true)

      // Step 3: Loyalty Program (already valid by default)
      expect(result.current.validateLoyaltyProgram()).toBe(true)

      // All validations should pass
      expect(result.current.validateBusinessInfo()).toBe(true)
      expect(result.current.validateMpesaChannels()).toBe(true)
      expect(result.current.validateLoyaltyProgram()).toBe(true)
    })

    it('handles multiple channels with different types', () => {
      const { result } = renderHook(() => useOnboarding(), { wrapper })

      act(() => {
        // Add PayBill channel (primary)
        result.current.addMpesaChannel({
          name: "Main PayBill",
          shortcode: "174379",
          channel_type: "paybill",
          environment: "sandbox",
          consumer_key: "paybill_key",
          consumer_secret: "paybill_secret",
          is_primary: true
        })

        // Add Till channel
        result.current.addMpesaChannel({
          name: "Shop Till",
          shortcode: "123456",
          channel_type: "till",
          environment: "sandbox",
          consumer_key: "till_key",
          consumer_secret: "till_secret",
          is_primary: false
        })

        // Add Buy Goods channel
        result.current.addMpesaChannel({
          name: "Online Store",
          shortcode: "789012",
          channel_type: "buygoods",
          environment: "production",
          consumer_key: "buygoods_key",
          consumer_secret: "buygoods_secret",
          is_primary: false
        })
      })

      expect(result.current.data.mpesaChannels).toHaveLength(3)
      expect(result.current.validateMpesaChannels()).toBe(true)

      // Verify channel types
      const channelTypes = result.current.data.mpesaChannels.map(ch => ch.channel_type)
      expect(channelTypes).toContain("paybill")
      expect(channelTypes).toContain("till")
      expect(channelTypes).toContain("buygoods")

      // Verify only one primary
      const primaryChannels = result.current.data.mpesaChannels.filter(ch => ch.is_primary)
      expect(primaryChannels).toHaveLength(1)
      expect(primaryChannels[0].name).toBe("Main PayBill")
    })
  })
})
