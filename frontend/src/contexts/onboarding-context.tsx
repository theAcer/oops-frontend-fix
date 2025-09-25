"use client"

import React, { createContext, useContext, useState, useCallback } from "react"
import { toast } from "react-hot-toast"

export interface BusinessInfo {
  businessName: string
  ownerName: string
  email: string
  phone: string
  businessType: string
  businessAddress?: string
  businessDescription?: string
  website?: string
  taxId?: string
}

export interface MpesaChannelData {
  id?: number
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
  status?: string
}

export interface LoyaltyProgramConfig {
  name: string
  description: string
  points_per_shilling: number
  redemption_rate: number
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

export interface OnboardingData {
  businessInfo: BusinessInfo
  mpesaChannels: MpesaChannelData[]
  loyaltyProgram: LoyaltyProgramConfig
  currentMerchantId?: number
}

interface OnboardingContextType {
  data: OnboardingData
  updateBusinessInfo: (info: Partial<BusinessInfo>) => void
  addMpesaChannel: (channel: MpesaChannelData) => void
  updateMpesaChannel: (index: number, channel: Partial<MpesaChannelData>) => void
  removeMpesaChannel: (index: number) => void
  updateLoyaltyProgram: (config: Partial<LoyaltyProgramConfig>) => void
  setMerchantId: (id: number) => void
  resetOnboarding: () => void
  validateBusinessInfo: () => boolean
  validateMpesaChannels: () => boolean
  validateLoyaltyProgram: () => boolean
}

const defaultBusinessInfo: BusinessInfo = {
  businessName: "",
  ownerName: "",
  email: "",
  phone: "",
  businessType: "",
  businessAddress: "",
  businessDescription: "",
  website: "",
  taxId: ""
}

const defaultLoyaltyProgram: LoyaltyProgramConfig = {
  name: "Loyalty Rewards",
  description: "Earn points with every purchase and unlock exclusive rewards",
  points_per_shilling: 1,
  redemption_rate: 100, // 100 points = 1 KES
  tier_system_enabled: true,
  tiers: [
    {
      name: "Bronze",
      min_points: 0,
      multiplier: 1,
      benefits: ["Standard rewards", "Birthday bonus"]
    },
    {
      name: "Silver",
      min_points: 1000,
      multiplier: 1.2,
      benefits: ["20% bonus points", "Priority support", "Birthday bonus"]
    },
    {
      name: "Gold",
      min_points: 5000,
      multiplier: 1.5,
      benefits: ["50% bonus points", "VIP support", "Exclusive offers", "Birthday bonus"]
    },
    {
      name: "Platinum",
      min_points: 15000,
      multiplier: 2,
      benefits: ["Double points", "Personal account manager", "Early access", "Premium rewards"]
    }
  ],
  welcome_bonus: 100,
  referral_bonus: 200,
  birthday_bonus: 500
}

const defaultOnboardingData: OnboardingData = {
  businessInfo: defaultBusinessInfo,
  mpesaChannels: [],
  loyaltyProgram: defaultLoyaltyProgram
}

const OnboardingContext = createContext<OnboardingContextType | undefined>(undefined)

export function OnboardingProvider({ children }: { children: React.ReactNode }) {
  const [data, setData] = useState<OnboardingData>(defaultOnboardingData)

  const updateBusinessInfo = useCallback((info: Partial<BusinessInfo>) => {
    setData(prev => ({
      ...prev,
      businessInfo: { ...prev.businessInfo, ...info }
    }))
  }, [])

  const addMpesaChannel = useCallback((channel: MpesaChannelData) => {
    setData(prev => ({
      ...prev,
      mpesaChannels: [...prev.mpesaChannels, channel]
    }))
  }, [])

  const updateMpesaChannel = useCallback((index: number, channel: Partial<MpesaChannelData>) => {
    setData(prev => ({
      ...prev,
      mpesaChannels: prev.mpesaChannels.map((ch, i) => 
        i === index ? { ...ch, ...channel } : ch
      )
    }))
  }, [])

  const removeMpesaChannel = useCallback((index: number) => {
    setData(prev => ({
      ...prev,
      mpesaChannels: prev.mpesaChannels.filter((_, i) => i !== index)
    }))
  }, [])

  const updateLoyaltyProgram = useCallback((config: Partial<LoyaltyProgramConfig>) => {
    setData(prev => ({
      ...prev,
      loyaltyProgram: { ...prev.loyaltyProgram, ...config }
    }))
  }, [])

  const setMerchantId = useCallback((id: number) => {
    setData(prev => ({
      ...prev,
      currentMerchantId: id
    }))
  }, [])

  const resetOnboarding = useCallback(() => {
    setData(defaultOnboardingData)
  }, [])

  const validateBusinessInfo = useCallback((): boolean => {
    const { businessName, ownerName, email, phone, businessType } = data.businessInfo
    
    if (!businessName.trim()) {
      toast.error("Business name is required")
      return false
    }
    
    if (!ownerName.trim()) {
      toast.error("Owner name is required")
      return false
    }
    
    if (!email.trim() || !/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(email)) {
      toast.error("Valid email address is required")
      return false
    }
    
    if (!phone.trim() || !/^254\d{9}$/.test(phone.replace(/\s+/g, ""))) {
      toast.error("Valid Kenyan phone number is required (254XXXXXXXXX)")
      return false
    }
    
    if (!businessType) {
      toast.error("Business type is required")
      return false
    }
    
    return true
  }, [data.businessInfo])

  const validateMpesaChannels = useCallback((): boolean => {
    if (data.mpesaChannels.length === 0) {
      toast.error("At least one M-Pesa channel is required")
      return false
    }

    for (const [index, channel] of data.mpesaChannels.entries()) {
      if (!channel.name.trim()) {
        toast.error(`Channel ${index + 1}: Name is required`)
        return false
      }
      
      if (!channel.shortcode.trim()) {
        toast.error(`Channel ${index + 1}: Shortcode is required`)
        return false
      }
      
      if (!channel.consumer_key.trim()) {
        toast.error(`Channel ${index + 1}: Consumer key is required`)
        return false
      }
      
      if (!channel.consumer_secret.trim()) {
        toast.error(`Channel ${index + 1}: Consumer secret is required`)
        return false
      }

      // Validate shortcode format based on channel type
      if (channel.channel_type === "paybill" && !/^\d{5,7}$/.test(channel.shortcode)) {
        toast.error(`Channel ${index + 1}: PayBill shortcode should be 5-7 digits`)
        return false
      }
      
      if (channel.channel_type === "till" && !/^\d{5,7}$/.test(channel.shortcode)) {
        toast.error(`Channel ${index + 1}: Till number should be 5-7 digits`)
        return false
      }
      
      if (channel.channel_type === "buygoods" && !/^\d{5,7}$/.test(channel.shortcode)) {
        toast.error(`Channel ${index + 1}: Buy Goods number should be 5-7 digits`)
        return false
      }

      // Validate URLs if provided
      if (channel.validation_url && !/^https?:\/\/.+/.test(channel.validation_url)) {
        toast.error(`Channel ${index + 1}: Invalid validation URL`)
        return false
      }
      
      if (channel.confirmation_url && !/^https?:\/\/.+/.test(channel.confirmation_url)) {
        toast.error(`Channel ${index + 1}: Invalid confirmation URL`)
        return false
      }
    }

    // Ensure only one primary channel
    const primaryChannels = data.mpesaChannels.filter(ch => ch.is_primary)
    if (primaryChannels.length === 0) {
      toast.error("Please select one channel as primary")
      return false
    }
    
    if (primaryChannels.length > 1) {
      toast.error("Only one channel can be set as primary")
      return false
    }

    return true
  }, [data.mpesaChannels])

  const validateLoyaltyProgram = useCallback((): boolean => {
    const { name, description, points_per_shilling, redemption_rate } = data.loyaltyProgram
    
    if (!name.trim()) {
      toast.error("Loyalty program name is required")
      return false
    }
    
    if (!description.trim()) {
      toast.error("Loyalty program description is required")
      return false
    }
    
    if (points_per_shilling <= 0) {
      toast.error("Points per shilling must be greater than 0")
      return false
    }
    
    if (redemption_rate <= 0) {
      toast.error("Redemption rate must be greater than 0")
      return false
    }

    // Validate tiers if tier system is enabled
    if (data.loyaltyProgram.tier_system_enabled && data.loyaltyProgram.tiers) {
      for (const [index, tier] of data.loyaltyProgram.tiers.entries()) {
        if (!tier.name.trim()) {
          toast.error(`Tier ${index + 1}: Name is required`)
          return false
        }
        
        if (tier.min_points < 0) {
          toast.error(`Tier ${index + 1}: Minimum points cannot be negative`)
          return false
        }
        
        if (tier.multiplier <= 0) {
          toast.error(`Tier ${index + 1}: Multiplier must be greater than 0`)
          return false
        }
      }

      // Ensure tiers are in ascending order of min_points
      const sortedTiers = [...data.loyaltyProgram.tiers].sort((a, b) => a.min_points - b.min_points)
      for (let i = 0; i < sortedTiers.length; i++) {
        if (sortedTiers[i].min_points !== data.loyaltyProgram.tiers[i].min_points) {
          toast.error("Tiers should be ordered by minimum points (ascending)")
          return false
        }
      }
    }
    
    return true
  }, [data.loyaltyProgram])

  const contextValue: OnboardingContextType = {
    data,
    updateBusinessInfo,
    addMpesaChannel,
    updateMpesaChannel,
    removeMpesaChannel,
    updateLoyaltyProgram,
    setMerchantId,
    resetOnboarding,
    validateBusinessInfo,
    validateMpesaChannels,
    validateLoyaltyProgram
  }

  return (
    <OnboardingContext.Provider value={contextValue}>
      {children}
    </OnboardingContext.Provider>
  )
}

export function useOnboarding() {
  const context = useContext(OnboardingContext)
  if (context === undefined) {
    throw new Error("useOnboarding must be used within an OnboardingProvider")
  }
  return context
}
