/**
 * @jest-environment jsdom
 */

import React from 'react'
import { render, screen, fireEvent, waitFor, act } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import { jest } from '@jest/globals'

// Mock Next.js router
const mockPush = jest.fn()
const mockRouter = {
  push: mockPush,
  pathname: '/onboarding',
  query: {},
  asPath: '/onboarding'
}

jest.mock('next/navigation', () => ({
  useRouter: () => mockRouter
}))

// Mock auth context
const mockUser = {
  id: 1,
  email: 'test@example.com',
  name: 'Test User',
  merchant_id: null,
  onboarding_completed: false
}

const mockAuthContext = {
  user: mockUser,
  login: jest.fn(),
  register: jest.fn(),
  registerMerchant: jest.fn(),
  logout: jest.fn(),
  loading: false
}

jest.mock('@/contexts/auth-context', () => ({
  useAuth: () => mockAuthContext
}))

// Mock API service
const mockOnboardingService = {
  createMerchant: jest.fn(),
  linkUserToMerchant: jest.fn(),
  createMpesaChannels: jest.fn(),
  createLoyaltyProgram: jest.fn(),
  completeOnboarding: jest.fn(),
  verifyMpesaChannel: jest.fn(),
  testMpesaChannel: jest.fn()
}

jest.mock('@/services/onboarding-service', () => ({
  onboardingService: mockOnboardingService
}))

// Mock toast
jest.mock('react-hot-toast', () => ({
  toast: {
    success: jest.fn(),
    error: jest.fn(),
    loading: jest.fn()
  }
}))

import OnboardingPage from '@/app/onboarding/page'
import { OnboardingProvider } from '@/contexts/onboarding-context'

// Test wrapper component
const TestWrapper = ({ children }: { children: React.ReactNode }) => (
  <OnboardingProvider>
    {children}
  </OnboardingProvider>
)

describe('Onboarding Flow', () => {
  beforeEach(() => {
    jest.clearAllMocks()
  })

  describe('OnboardingPage', () => {
    it('renders onboarding page with progress overview', () => {
      render(
        <TestWrapper>
          <OnboardingPage />
        </TestWrapper>
      )

      expect(screen.getByText('Welcome to Zidisha Loyalty Platform')).toBeInTheDocument()
      expect(screen.getByText('Setup Progress')).toBeInTheDocument()
      expect(screen.getByText('Business Information')).toBeInTheDocument()
      expect(screen.getByText('M-Pesa Integration')).toBeInTheDocument()
      expect(screen.getByText('Loyalty Program')).toBeInTheDocument()
      expect(screen.getByText('Launch')).toBeInTheDocument()
    })

    it('redirects authenticated users with completed onboarding', () => {
      const completedUser = {
        ...mockUser,
        merchant_id: 123,
        onboarding_completed: true
      }

      const mockAuthContextCompleted = {
        ...mockAuthContext,
        user: completedUser
      }

      jest.mocked(require('@/contexts/auth-context').useAuth).mockReturnValue(mockAuthContextCompleted)

      render(
        <TestWrapper>
          <OnboardingPage />
        </TestWrapper>
      )

      expect(mockPush).toHaveBeenCalledWith('/dashboard')
    })

    it('shows correct progress percentage', () => {
      render(
        <TestWrapper>
          <OnboardingPage />
        </TestWrapper>
      )

      // Initially 0% complete
      expect(screen.getByText('0% Complete')).toBeInTheDocument()
    })
  })

  describe('Business Information Step', () => {
    it('renders business info form fields', () => {
      render(
        <TestWrapper>
          <OnboardingPage />
        </TestWrapper>
      )

      expect(screen.getByLabelText(/business name/i)).toBeInTheDocument()
      expect(screen.getByLabelText(/owner.*name/i)).toBeInTheDocument()
      expect(screen.getByLabelText(/business email/i)).toBeInTheDocument()
      expect(screen.getByLabelText(/business phone/i)).toBeInTheDocument()
      expect(screen.getByLabelText(/business type/i)).toBeInTheDocument()
    })

    it('validates required fields', async () => {
      const user = userEvent.setup()
      
      render(
        <TestWrapper>
          <OnboardingPage />
        </TestWrapper>
      )

      const continueButton = screen.getByText('Continue')
      await user.click(continueButton)

      await waitFor(() => {
        expect(screen.getByText(/business name is required/i)).toBeInTheDocument()
      })
    })

    it('validates email format', async () => {
      const user = userEvent.setup()
      
      render(
        <TestWrapper>
          <OnboardingPage />
        </TestWrapper>
      )

      const emailInput = screen.getByLabelText(/business email/i)
      await user.type(emailInput, 'invalid-email')

      const continueButton = screen.getByText('Continue')
      await user.click(continueButton)

      await waitFor(() => {
        expect(screen.getByText(/valid email address is required/i)).toBeInTheDocument()
      })
    })

    it('validates phone number format', async () => {
      const user = userEvent.setup()
      
      render(
        <TestWrapper>
          <OnboardingPage />
        </TestWrapper>
      )

      const phoneInput = screen.getByLabelText(/business phone/i)
      await user.type(phoneInput, '123456789')

      const continueButton = screen.getByText('Continue')
      await user.click(continueButton)

      await waitFor(() => {
        expect(screen.getByText(/valid kenyan phone number is required/i)).toBeInTheDocument()
      })
    })

    it('accepts valid business information', async () => {
      const user = userEvent.setup()
      
      render(
        <TestWrapper>
          <OnboardingPage />
        </TestWrapper>
      )

      // Fill in valid business information
      await user.type(screen.getByLabelText(/business name/i), 'Test Electronics Store')
      await user.type(screen.getByLabelText(/owner.*name/i), 'John Doe')
      await user.type(screen.getByLabelText(/business email/i), 'john@teststore.com')
      await user.type(screen.getByLabelText(/business phone/i), '254712345678')
      
      // Select business type
      const businessTypeSelect = screen.getByLabelText(/business type/i)
      await user.click(businessTypeSelect)
      await user.click(screen.getByText('Retail'))

      const continueButton = screen.getByText('Continue')
      await user.click(continueButton)

      // Should proceed to next step without validation errors
      await waitFor(() => {
        expect(screen.queryByText(/is required/i)).not.toBeInTheDocument()
      })
    })
  })

  describe('M-Pesa Setup Step', () => {
    beforeEach(async () => {
      // Navigate to M-Pesa setup step by completing business info
      const user = userEvent.setup()
      
      render(
        <TestWrapper>
          <OnboardingPage />
        </TestWrapper>
      )

      // Fill business info and proceed
      await user.type(screen.getByLabelText(/business name/i), 'Test Store')
      await user.type(screen.getByLabelText(/owner.*name/i), 'John Doe')
      await user.type(screen.getByLabelText(/business email/i), 'john@test.com')
      await user.type(screen.getByLabelText(/business phone/i), '254712345678')
      
      const businessTypeSelect = screen.getByLabelText(/business type/i)
      await user.click(businessTypeSelect)
      await user.click(screen.getByText('Retail'))
      
      await user.click(screen.getByText('Continue'))

      // Wait for M-Pesa step to load
      await waitFor(() => {
        expect(screen.getByText('Connect Your M-Pesa Channels')).toBeInTheDocument()
      })
    })

    it('shows add channel form when no channels exist', () => {
      expect(screen.getByText('Add Your First Channel')).toBeInTheDocument()
    })

    it('validates M-Pesa channel form fields', async () => {
      const user = userEvent.setup()

      // Click add channel button
      await user.click(screen.getByText('Add Your First Channel'))

      // Try to add without filling required fields
      await user.click(screen.getByText('Add Channel'))

      await waitFor(() => {
        expect(screen.getByText(/channel name is required/i)).toBeInTheDocument()
      })
    })

    it('adds M-Pesa channel successfully', async () => {
      const user = userEvent.setup()

      // Click add channel button
      await user.click(screen.getByText('Add Your First Channel'))

      // Fill channel information
      await user.type(screen.getByLabelText(/channel name/i), 'Main PayBill')
      await user.type(screen.getByLabelText(/shortcode/i), '174379')
      await user.type(screen.getByLabelText(/consumer key/i), 'test_consumer_key')
      await user.type(screen.getByLabelText(/consumer secret/i), 'test_consumer_secret')

      // Add channel
      await user.click(screen.getByText('Add Channel'))

      await waitFor(() => {
        expect(screen.getByText('M-Pesa channel added successfully')).toBeInTheDocument()
        expect(screen.getByText('Main PayBill')).toBeInTheDocument()
      })
    })

    it('validates shortcode format for different channel types', async () => {
      const user = userEvent.setup()

      await user.click(screen.getByText('Add Your First Channel'))

      // Fill basic info with invalid shortcode
      await user.type(screen.getByLabelText(/channel name/i), 'Test Channel')
      await user.type(screen.getByLabelText(/shortcode/i), '123') // Too short
      await user.type(screen.getByLabelText(/consumer key/i), 'test_key')
      await user.type(screen.getByLabelText(/consumer secret/i), 'test_secret')

      await user.click(screen.getByText('Add Channel'))

      await waitFor(() => {
        expect(screen.getByText(/shortcode should be 5-7 digits/i)).toBeInTheDocument()
      })
    })

    it('ensures only one primary channel', async () => {
      const user = userEvent.setup()

      // Add first channel (will be primary by default)
      await user.click(screen.getByText('Add Your First Channel'))
      await user.type(screen.getByLabelText(/channel name/i), 'Channel 1')
      await user.type(screen.getByLabelText(/shortcode/i), '174379')
      await user.type(screen.getByLabelText(/consumer key/i), 'key1')
      await user.type(screen.getByLabelText(/consumer secret/i), 'secret1')
      await user.click(screen.getByText('Add Channel'))

      await waitFor(() => {
        expect(screen.getByText('Channel 1')).toBeInTheDocument()
      })

      // Add second channel and try to make it primary
      await user.click(screen.getByText('Add Channel'))
      await user.type(screen.getByLabelText(/channel name/i), 'Channel 2')
      await user.type(screen.getByLabelText(/shortcode/i), '123456')
      await user.type(screen.getByLabelText(/consumer key/i), 'key2')
      await user.type(screen.getByLabelText(/consumer secret/i), 'secret2')
      
      // Try to set as primary
      const primarySwitch = screen.getByLabelText(/primary channel/i)
      await user.click(primarySwitch)
      
      await user.click(screen.getByText('Add Channel'))

      // Should validate that only one primary is allowed
      await waitFor(() => {
        expect(screen.getByText(/only one channel can be set as primary/i)).toBeInTheDocument()
      })
    })
  })

  describe('Loyalty Program Configuration Step', () => {
    beforeEach(async () => {
      // Navigate to loyalty config step
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

      // Complete M-Pesa setup
      await waitFor(() => {
        expect(screen.getByText('Add Your First Channel')).toBeInTheDocument()
      })
      
      await user.click(screen.getByText('Add Your First Channel'))
      await user.type(screen.getByLabelText(/channel name/i), 'Test Channel')
      await user.type(screen.getByLabelText(/shortcode/i), '174379')
      await user.type(screen.getByLabelText(/consumer key/i), 'test_key')
      await user.type(screen.getByLabelText(/consumer secret/i), 'test_secret')
      await user.click(screen.getByText('Add Channel'))
      
      await waitFor(() => {
        expect(screen.getByText('Continue')).toBeInTheDocument()
      })
      await user.click(screen.getByText('Continue'))

      // Wait for loyalty config step
      await waitFor(() => {
        expect(screen.getByText('Configure Your Loyalty Program')).toBeInTheDocument()
      })
    })

    it('renders loyalty program configuration form', () => {
      expect(screen.getByLabelText(/program name/i)).toBeInTheDocument()
      expect(screen.getByLabelText(/program description/i)).toBeInTheDocument()
      expect(screen.getByLabelText(/points per kes/i)).toBeInTheDocument()
      expect(screen.getByLabelText(/redemption rate/i)).toBeInTheDocument()
    })

    it('validates loyalty program fields', async () => {
      const user = userEvent.setup()

      // Clear program name and try to continue
      const programNameInput = screen.getByLabelText(/program name/i)
      await user.clear(programNameInput)

      await user.click(screen.getByText('Continue'))

      await waitFor(() => {
        expect(screen.getByText(/loyalty program name is required/i)).toBeInTheDocument()
      })
    })

    it('configures tier system', async () => {
      const user = userEvent.setup()

      // Tier system should be enabled by default
      expect(screen.getByText('Bronze')).toBeInTheDocument()
      expect(screen.getByText('Silver')).toBeInTheDocument()
      expect(screen.getByText('Gold')).toBeInTheDocument()
      expect(screen.getByText('Platinum')).toBeInTheDocument()

      // Add a new tier
      await user.click(screen.getByText('Add Tier'))

      await waitFor(() => {
        expect(screen.getByText('Tier 5')).toBeInTheDocument()
      })
    })

    it('validates tier configuration', async () => {
      const user = userEvent.setup()

      // Try to set negative minimum points for a tier
      const minPointsInputs = screen.getAllByLabelText(/minimum points/i)
      await user.clear(minPointsInputs[0])
      await user.type(minPointsInputs[0], '-100')

      await user.click(screen.getByText('Continue'))

      await waitFor(() => {
        expect(screen.getByText(/minimum points cannot be negative/i)).toBeInTheDocument()
      })
    })
  })

  describe('Launch Step', () => {
    beforeEach(async () => {
      // Complete all previous steps to reach launch
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

      // Complete M-Pesa setup
      await waitFor(() => screen.getByText('Add Your First Channel'))
      await user.click(screen.getByText('Add Your First Channel'))
      await user.type(screen.getByLabelText(/channel name/i), 'Test Channel')
      await user.type(screen.getByLabelText(/shortcode/i), '174379')
      await user.type(screen.getByLabelText(/consumer key/i), 'test_key')
      await user.type(screen.getByLabelText(/consumer secret/i), 'test_secret')
      await user.click(screen.getByText('Add Channel'))
      await user.click(screen.getByText('Continue'))

      // Complete loyalty config
      await waitFor(() => screen.getByText('Configure Your Loyalty Program'))
      await user.click(screen.getByText('Continue'))

      // Wait for launch step
      await waitFor(() => {
        expect(screen.getByText('Ready to Launch Your Platform?')).toBeInTheDocument()
      })
    })

    it('shows pre-launch checklist with all items complete', () => {
      expect(screen.getByText('Pre-launch Checklist')).toBeInTheDocument()
      
      const completeItems = screen.getAllByText('Complete')
      expect(completeItems).toHaveLength(3) // Business, M-Pesa, Loyalty
    })

    it('shows configuration summary', () => {
      expect(screen.getByText('Configuration Summary')).toBeInTheDocument()
      expect(screen.getByText('Test Store')).toBeInTheDocument()
      expect(screen.getByText('John Doe')).toBeInTheDocument()
      expect(screen.getByText('Test Channel')).toBeInTheDocument()
    })

    it('launches platform successfully', async () => {
      const user = userEvent.setup()

      // Mock successful API responses
      mockOnboardingService.completeOnboarding.mockResolvedValue({
        merchant: { id: 123, business_name: 'Test Store' },
        channels: [{ id: 456, name: 'Test Channel' }],
        loyalty_program: { id: 789, name: 'Loyalty Rewards' },
        verification_results: [{ channel_id: 456, verified: true }]
      })

      await user.click(screen.getByText('Launch My Loyalty Platform'))

      // Should show launching progress
      await waitFor(() => {
        expect(screen.getByText('Launching Platform...')).toBeInTheDocument()
      })

      // Should complete and show success
      await waitFor(() => {
        expect(screen.getByText('Platform Launched Successfully!')).toBeInTheDocument()
      }, { timeout: 10000 })

      expect(mockOnboardingService.completeOnboarding).toHaveBeenCalled()
    })

    it('handles launch errors gracefully', async () => {
      const user = userEvent.setup()

      // Mock API error
      mockOnboardingService.completeOnboarding.mockRejectedValue(
        new Error('API Error')
      )

      await user.click(screen.getByText('Launch My Loyalty Platform'))

      await waitFor(() => {
        expect(screen.getByText(/launch failed/i)).toBeInTheDocument()
      })
    })
  })

  describe('Navigation and Progress Tracking', () => {
    it('updates progress as steps are completed', async () => {
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

      // Should show 25% complete (1 of 4 steps)
      await waitFor(() => {
        expect(screen.getByText('25% Complete')).toBeInTheDocument()
      })
    })

    it('allows clicking on accessible steps to navigate', async () => {
      const user = userEvent.setup()
      
      render(
        <TestWrapper>
          <OnboardingPage />
        </TestWrapper>
      )

      // Complete first step
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
    })
  })

  describe('Error Handling and Edge Cases', () => {
    it('handles network errors gracefully', async () => {
      const user = userEvent.setup()
      
      render(
        <TestWrapper>
          <OnboardingPage />
        </TestWrapper>
      )

      // Mock network error
      mockOnboardingService.linkUserToMerchant.mockRejectedValue(
        new Error('Network Error')
      )

      // Complete all steps and try to launch
      // ... (complete steps code)

      // Should show error message
      await waitFor(() => {
        expect(screen.getByText(/an error occurred/i)).toBeInTheDocument()
      })
    })

    it('validates form data before API calls', async () => {
      const user = userEvent.setup()
      
      render(
        <TestWrapper>
          <OnboardingPage />
        </TestWrapper>
      )

      // Try to proceed without filling required fields
      await user.click(screen.getByText('Continue'))

      // Should not make API calls
      expect(mockOnboardingService.linkUserToMerchant).not.toHaveBeenCalled()
    })

    it('handles partial completion and resume', () => {
      // Test that user can resume onboarding from where they left off
      const partialUser = {
        ...mockUser,
        onboarding_step: 'mpesa-setup',
        onboarding_progress: 25
      }

      const mockAuthContextPartial = {
        ...mockAuthContext,
        user: partialUser
      }

      jest.mocked(require('@/contexts/auth-context').useAuth).mockReturnValue(mockAuthContextPartial)

      render(
        <TestWrapper>
          <OnboardingPage />
        </TestWrapper>
      )

      // Should show 25% progress
      expect(screen.getByText('25% Complete')).toBeInTheDocument()
    })
  })
})
