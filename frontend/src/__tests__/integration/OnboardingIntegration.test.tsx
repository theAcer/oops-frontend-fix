/**
 * @jest-environment jsdom
 */

import React from 'react'
import { render, screen, fireEvent, waitFor } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import { jest } from '@jest/globals'

// Mock Next.js router
const mockPush = jest.fn()
jest.mock('next/navigation', () => ({
  useRouter: () => ({ push: mockPush })
}))

// Mock auth context
const mockAuthContext = {
  user: { id: 1, email: 'test@example.com', merchant_id: null, onboarding_completed: false },
  login: jest.fn(),
  register: jest.fn(),
  registerMerchant: jest.fn(),
  logout: jest.fn(),
  loading: false
}

jest.mock('@/contexts/auth-context', () => ({
  useAuth: () => mockAuthContext
}))

// Mock onboarding service
const mockOnboardingService = {
  completeOnboarding: jest.fn(),
  createMerchant: jest.fn(),
  createMpesaChannels: jest.fn(),
  createLoyaltyProgram: jest.fn(),
  verifyMpesaChannel: jest.fn(),
  testMpesaChannel: jest.fn(),
  getOnboardingStatus: jest.fn(),
  updateOnboardingProgress: jest.fn(),
  markOnboardingCompleted: jest.fn()
}

jest.mock('@/services/onboarding-service', () => ({
  onboardingService: mockOnboardingService
}))

// Mock toast
const mockToast = {
  success: jest.fn(),
  error: jest.fn(),
  loading: jest.fn()
}

jest.mock('react-hot-toast', () => ({
  toast: mockToast
}))

import OnboardingPage from '@/app/onboarding/page'
import { OnboardingProvider } from '@/contexts/onboarding-context'

const TestWrapper = ({ children }: { children: React.ReactNode }) => (
  <OnboardingProvider>
    {children}
  </OnboardingProvider>
)

describe('Onboarding Integration Tests', () => {
  beforeEach(() => {
    jest.clearAllMocks()
  })

  describe('Complete Onboarding Flow', () => {
    it('completes full onboarding flow successfully', async () => {
      const user = userEvent.setup()
      
      // Mock successful API responses
      mockOnboardingService.completeOnboarding.mockResolvedValue({
        merchant: { id: 123, business_name: 'Test Store' },
        channels: [{ id: 456, name: 'Test Channel', verified: true }],
        loyalty_program: { id: 789, name: 'VIP Rewards' },
        verification_results: [{ channel_id: 456, verified: true }]
      })

      render(
        <TestWrapper>
          <OnboardingPage />
        </TestWrapper>
      )

      // Step 1: Complete Business Information
      expect(screen.getByText('Business Information')).toBeInTheDocument()
      
      await user.type(screen.getByLabelText(/business name/i), 'Test Electronics Store')
      await user.type(screen.getByLabelText(/owner.*name/i), 'John Doe')
      await user.type(screen.getByLabelText(/business email/i), 'john@teststore.com')
      await user.type(screen.getByLabelText(/business phone/i), '254712345678')
      
      // Select business type
      const businessTypeSelect = screen.getByLabelText(/business type/i)
      await user.click(businessTypeSelect)
      await user.click(screen.getByText('Retail'))

      // Optional fields
      await user.type(screen.getByLabelText(/business address/i), '123 Test Street, Nairobi')
      await user.type(screen.getByLabelText(/business description/i), 'Electronics and gadgets store')
      await user.type(screen.getByLabelText(/website/i), 'https://teststore.com')

      await user.click(screen.getByText('Continue'))

      // Step 2: M-Pesa Channel Setup
      await waitFor(() => {
        expect(screen.getByText('Connect Your M-Pesa Channels')).toBeInTheDocument()
      })

      // Add first M-Pesa channel
      await user.click(screen.getByText('Add Your First Channel'))

      await user.type(screen.getByLabelText(/channel name/i), 'Main PayBill')
      await user.type(screen.getByLabelText(/shortcode/i), '174379')
      
      // Select channel type
      const channelTypeSelect = screen.getByLabelText(/channel type/i)
      await user.click(channelTypeSelect)
      await user.click(screen.getByText('PayBill'))

      // Add credentials
      await user.type(screen.getByLabelText(/consumer key/i), 'test_consumer_key_123')
      await user.type(screen.getByLabelText(/consumer secret/i), 'test_consumer_secret_456')
      await user.type(screen.getByLabelText(/passkey/i), 'test_passkey_789')

      // Add webhook URLs
      await user.type(screen.getByLabelText(/validation url/i), 'https://teststore.com/mpesa/validate')
      await user.type(screen.getByLabelText(/confirmation url/i), 'https://teststore.com/mpesa/confirm')

      // Add account mapping
      const accountMappingTextarea = screen.getByLabelText(/account mapping/i)
      await user.clear(accountMappingTextarea)
      await user.type(accountMappingTextarea, JSON.stringify({
        "default": "standard_loyalty",
        "VIP*": "vip_program",
        "STUDENT*": "student_program"
      }, null, 2))

      await user.click(screen.getByText('Add Channel'))

      await waitFor(() => {
        expect(screen.getByText('Main PayBill')).toBeInTheDocument()
        expect(mockToast.success).toHaveBeenCalledWith('M-Pesa channel added successfully')
      })

      // Add second channel (Till)
      await user.click(screen.getByText('Add Channel'))

      await user.type(screen.getByLabelText(/channel name/i), 'Shop Till')
      await user.type(screen.getByLabelText(/shortcode/i), '123456')
      
      const secondChannelTypeSelect = screen.getByLabelText(/channel type/i)
      await user.click(secondChannelTypeSelect)
      await user.click(screen.getByText('Till Number'))

      await user.type(screen.getByLabelText(/consumer key/i), 'till_consumer_key')
      await user.type(screen.getByLabelText(/consumer secret/i), 'till_consumer_secret')

      // Don't set as primary (first channel should remain primary)
      const primarySwitch = screen.getByLabelText(/primary channel/i)
      expect(primarySwitch).not.toBeChecked()

      await user.click(screen.getByText('Add Channel'))

      await waitFor(() => {
        expect(screen.getByText('Shop Till')).toBeInTheDocument()
      })

      // Continue to next step
      await user.click(screen.getByText('Continue'))

      // Step 3: Loyalty Program Configuration
      await waitFor(() => {
        expect(screen.getByText('Configure Your Loyalty Program')).toBeInTheDocument()
      })

      // Customize loyalty program
      const programNameInput = screen.getByLabelText(/program name/i)
      await user.clear(programNameInput)
      await user.type(programNameInput, 'VIP Electronics Rewards')

      const programDescInput = screen.getByLabelText(/program description/i)
      await user.clear(programDescInput)
      await user.type(programDescInput, 'Earn points with every electronics purchase and unlock exclusive tech deals')

      // Adjust points per shilling
      const pointsPerKesInput = screen.getByLabelText(/points per kes/i)
      await user.clear(pointsPerKesInput)
      await user.type(pointsPerKesInput, '2')

      // Adjust redemption rate
      const redemptionRateInput = screen.getByLabelText(/redemption rate/i)
      await user.clear(redemptionRateInput)
      await user.type(redemptionRateInput, '50')

      // Customize bonuses
      const welcomeBonusInput = screen.getByLabelText(/welcome bonus/i)
      await user.clear(welcomeBonusInput)
      await user.type(welcomeBonusInput, '200')

      const referralBonusInput = screen.getByLabelText(/referral bonus/i)
      await user.clear(referralBonusInput)
      await user.type(referralBonusInput, '500')

      const birthdayBonusInput = screen.getByLabelText(/birthday bonus/i)
      await user.clear(birthdayBonusInput)
      await user.type(birthdayBonusInput, '1000')

      // Verify tier system is enabled and customize tiers
      expect(screen.getByText('Bronze')).toBeInTheDocument()
      expect(screen.getByText('Silver')).toBeInTheDocument()
      expect(screen.getByText('Gold')).toBeInTheDocument()
      expect(screen.getByText('Platinum')).toBeInTheDocument()

      // Add a custom tier
      await user.click(screen.getByText('Add Tier'))

      await waitFor(() => {
        expect(screen.getByText('Tier 5')).toBeInTheDocument()
      })

      // Edit the new tier
      const tierNameInputs = screen.getAllByLabelText(/minimum points/i)
      const newTierMinPoints = tierNameInputs[tierNameInputs.length - 1]
      await user.clear(newTierMinPoints)
      await user.type(newTierMinPoints, '25000')

      const tierMultiplierInputs = screen.getAllByLabelText(/points multiplier/i)
      const newTierMultiplier = tierMultiplierInputs[tierMultiplierInputs.length - 1]
      await user.clear(newTierMultiplier)
      await user.type(newTierMultiplier, '3')

      await user.click(screen.getByText('Continue'))

      // Step 4: Launch
      await waitFor(() => {
        expect(screen.getByText('Ready to Launch Your Platform?')).toBeInTheDocument()
      })

      // Verify pre-launch checklist shows all complete
      const completeItems = screen.getAllByText('Complete')
      expect(completeItems).toHaveLength(3) // Business, M-Pesa, Loyalty

      // Verify configuration summary
      expect(screen.getByText('Configuration Summary')).toBeInTheDocument()
      expect(screen.getByText('Test Electronics Store')).toBeInTheDocument()
      expect(screen.getByText('John Doe')).toBeInTheDocument()
      expect(screen.getByText('john@teststore.com')).toBeInTheDocument()
      expect(screen.getByText('Main PayBill')).toBeInTheDocument()
      expect(screen.getByText('Shop Till')).toBeInTheDocument()
      expect(screen.getByText('VIP Electronics Rewards')).toBeInTheDocument()

      // Launch the platform
      await user.click(screen.getByText('Launch My Loyalty Platform'))

      // Should show launching progress
      await waitFor(() => {
        expect(screen.getByText('Launching Platform...')).toBeInTheDocument()
      })

      // Wait for completion
      await waitFor(() => {
        expect(screen.getByText('Platform Launched Successfully!')).toBeInTheDocument()
      }, { timeout: 15000 })

      // Verify API was called with correct data
      expect(mockOnboardingService.completeOnboarding).toHaveBeenCalledWith(
        expect.objectContaining({
          businessName: 'Test Electronics Store',
          ownerName: 'John Doe',
          email: 'john@teststore.com',
          phone: '254712345678',
          businessType: 'retail'
        }),
        expect.arrayContaining([
          expect.objectContaining({
            name: 'Main PayBill',
            shortcode: '174379',
            channel_type: 'paybill',
            is_primary: true
          }),
          expect.objectContaining({
            name: 'Shop Till',
            shortcode: '123456',
            channel_type: 'till',
            is_primary: false
          })
        ]),
        expect.objectContaining({
          name: 'VIP Electronics Rewards',
          points_per_shilling: 2,
          redemption_rate: 50,
          welcome_bonus: 200,
          referral_bonus: 500,
          birthday_bonus: 1000
        }),
        true // linkToUser
      )

      // Should show success summary
      expect(screen.getByText('Launch Summary')).toBeInTheDocument()
      expect(screen.getByText('Merchant Created')).toBeInTheDocument()
      expect(screen.getByText('2 Channels')).toBeInTheDocument()
      expect(screen.getByText('Loyalty Program')).toBeInTheDocument()

      // Should show next steps
      expect(screen.getByText('Next Steps')).toBeInTheDocument()
      expect(screen.getByText('Invite Your Team')).toBeInTheDocument()
      expect(screen.getByText('Test Your Integration')).toBeInTheDocument()
      expect(screen.getByText('Launch Marketing Campaign')).toBeInTheDocument()

      // Click go to dashboard
      await user.click(screen.getByText('Go to Dashboard'))

      // Should redirect to dashboard
      expect(mockPush).toHaveBeenCalledWith('/dashboard')
    }, 30000) // Increase timeout for this comprehensive test

    it('handles validation errors during onboarding', async () => {
      const user = userEvent.setup()
      
      render(
        <TestWrapper>
          <OnboardingPage />
        </TestWrapper>
      )

      // Try to continue without filling business info
      await user.click(screen.getByText('Continue'))

      await waitFor(() => {
        expect(mockToast.error).toHaveBeenCalledWith('Business name is required')
      })

      // Fill partial info with invalid email
      await user.type(screen.getByLabelText(/business name/i), 'Test Store')
      await user.type(screen.getByLabelText(/owner.*name/i), 'John Doe')
      await user.type(screen.getByLabelText(/business email/i), 'invalid-email')
      await user.type(screen.getByLabelText(/business phone/i), '254712345678')

      const businessTypeSelect = screen.getByLabelText(/business type/i)
      await user.click(businessTypeSelect)
      await user.click(screen.getByText('Retail'))

      await user.click(screen.getByText('Continue'))

      await waitFor(() => {
        expect(mockToast.error).toHaveBeenCalledWith('Valid email address is required')
      })

      // Fix email and continue
      const emailInput = screen.getByLabelText(/business email/i)
      await user.clear(emailInput)
      await user.type(emailInput, 'john@test.com')

      await user.click(screen.getByText('Continue'))

      // Should proceed to M-Pesa step
      await waitFor(() => {
        expect(screen.getByText('Connect Your M-Pesa Channels')).toBeInTheDocument()
      })

      // Try to continue without adding channels
      await user.click(screen.getByText('Continue'))

      await waitFor(() => {
        expect(mockToast.error).toHaveBeenCalledWith('At least one M-Pesa channel is required')
      })
    })

    it('handles API errors during launch', async () => {
      const user = userEvent.setup()
      
      // Mock API failure
      mockOnboardingService.completeOnboarding.mockRejectedValue(
        new Error('Merchant creation failed')
      )

      render(
        <TestWrapper>
          <OnboardingPage />
        </TestWrapper>
      )

      // Complete all steps quickly
      await user.type(screen.getByLabelText(/business name/i), 'Test Store')
      await user.type(screen.getByLabelText(/owner.*name/i), 'John Doe')
      await user.type(screen.getByLabelText(/business email/i), 'john@test.com')
      await user.type(screen.getByLabelText(/business phone/i), '254712345678')
      
      const businessTypeSelect = screen.getByLabelText(/business type/i)
      await user.click(businessTypeSelect)
      await user.click(screen.getByText('Retail'))
      await user.click(screen.getByText('Continue'))

      // Add M-Pesa channel
      await waitFor(() => screen.getByText('Add Your First Channel'))
      await user.click(screen.getByText('Add Your First Channel'))
      await user.type(screen.getByLabelText(/channel name/i), 'Test Channel')
      await user.type(screen.getByLabelText(/shortcode/i), '174379')
      await user.type(screen.getByLabelText(/consumer key/i), 'test_key')
      await user.type(screen.getByLabelText(/consumer secret/i), 'test_secret')
      await user.click(screen.getByText('Add Channel'))
      await user.click(screen.getByText('Continue'))

      // Continue through loyalty config
      await waitFor(() => screen.getByText('Configure Your Loyalty Program'))
      await user.click(screen.getByText('Continue'))

      // Try to launch
      await waitFor(() => screen.getByText('Launch My Loyalty Platform'))
      await user.click(screen.getByText('Launch My Loyalty Platform'))

      // Should show error
      await waitFor(() => {
        expect(mockToast.error).toHaveBeenCalledWith('Launch failed. Please try again.')
      })

      // Should still be on launch step
      expect(screen.getByText('Ready to Launch Your Platform?')).toBeInTheDocument()
    })

    it('allows navigation between completed steps', async () => {
      const user = userEvent.setup()
      
      render(
        <TestWrapper>
          <OnboardingPage />
        </TestWrapper>
      )

      // Complete business info
      await user.type(screen.getByLabelText(/business name/i), 'Test Store')
      await user.type(screen.getByLabelText(/owner.*name/i), 'John Doe')
      await user.type(screen.getByLabelText(/business email/i), 'john@test.com')
      await user.type(screen.getByLabelText(/business phone/i), '254712345678')
      
      const businessTypeSelect = screen.getByLabelText(/business type/i)
      await user.click(businessTypeSelect)
      await user.click(screen.getByText('Retail'))
      await user.click(screen.getByText('Continue'))

      // Should be on M-Pesa step
      await waitFor(() => {
        expect(screen.getByText('Connect Your M-Pesa Channels')).toBeInTheDocument()
      })

      // Click back to business info step
      const businessInfoStep = screen.getByText('Business Information')
      await user.click(businessInfoStep)

      // Should navigate back
      await waitFor(() => {
        expect(screen.getByText('Tell us about your business')).toBeInTheDocument()
      })

      // Business info should be preserved
      expect(screen.getByDisplayValue('Test Store')).toBeInTheDocument()
      expect(screen.getByDisplayValue('John Doe')).toBeInTheDocument()
      expect(screen.getByDisplayValue('john@test.com')).toBeInTheDocument()
    })
  })

  describe('Progress Tracking', () => {
    it('updates progress percentage as steps are completed', async () => {
      const user = userEvent.setup()
      
      render(
        <TestWrapper>
          <OnboardingPage />
        </TestWrapper>
      )

      // Initially 0%
      expect(screen.getByText('0% Complete')).toBeInTheDocument()

      // Complete business info
      await user.type(screen.getByLabelText(/business name/i), 'Test Store')
      await user.type(screen.getByLabelText(/owner.*name/i), 'John Doe')
      await user.type(screen.getByLabelText(/business email/i), 'john@test.com')
      await user.type(screen.getByLabelText(/business phone/i), '254712345678')
      
      const businessTypeSelect = screen.getByLabelText(/business type/i)
      await user.click(businessTypeSelect)
      await user.click(screen.getByText('Retail'))
      await user.click(screen.getByText('Continue'))

      // Should show 25% complete
      await waitFor(() => {
        expect(screen.getByText('25% Complete')).toBeInTheDocument()
      })

      // Complete M-Pesa setup
      await waitFor(() => screen.getByText('Add Your First Channel'))
      await user.click(screen.getByText('Add Your First Channel'))
      await user.type(screen.getByLabelText(/channel name/i), 'Test Channel')
      await user.type(screen.getByLabelText(/shortcode/i), '174379')
      await user.type(screen.getByLabelText(/consumer key/i), 'test_key')
      await user.type(screen.getByLabelText(/consumer secret/i), 'test_secret')
      await user.click(screen.getByText('Add Channel'))
      await user.click(screen.getByText('Continue'))

      // Should show 50% complete
      await waitFor(() => {
        expect(screen.getByText('50% Complete')).toBeInTheDocument()
      })

      // Complete loyalty config
      await waitFor(() => screen.getByText('Configure Your Loyalty Program'))
      await user.click(screen.getByText('Continue'))

      // Should show 75% complete
      await waitFor(() => {
        expect(screen.getByText('75% Complete')).toBeInTheDocument()
      })
    })

    it('shows step completion status correctly', async () => {
      const user = userEvent.setup()
      
      render(
        <TestWrapper>
          <OnboardingPage />
        </TestWrapper>
      )

      // Initially no steps completed
      expect(screen.queryByText('✓')).not.toBeInTheDocument()

      // Complete first step
      await user.type(screen.getByLabelText(/business name/i), 'Test Store')
      await user.type(screen.getByLabelText(/owner.*name/i), 'John Doe')
      await user.type(screen.getByLabelText(/business email/i), 'john@test.com')
      await user.type(screen.getByLabelText(/business phone/i), '254712345678')
      
      const businessTypeSelect = screen.getByLabelText(/business type/i)
      await user.click(businessTypeSelect)
      await user.click(screen.getByText('Retail'))
      await user.click(screen.getByText('Continue'))

      // First step should show as completed
      await waitFor(() => {
        const completedSteps = screen.getAllByText('✓')
        expect(completedSteps).toHaveLength(1)
      })
    })
  })
})
