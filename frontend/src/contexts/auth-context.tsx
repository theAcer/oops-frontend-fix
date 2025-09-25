"use client"

import type React from "react"
import { createContext, useContext, useEffect, useState } from "react"
import { useRouter } from "next/navigation"
import { apiService } from "@/services/api-service" // Import apiService
import { UserResponse, MerchantCreateRequest } from "@/types/api" // Import UserResponse and MerchantCreateRequest
import { BusinessType } from "@/types/enums" // Import BusinessType

interface User extends UserResponse {} // Extend UserResponse for consistency

interface AuthContextType {
  user: User | null
  isMerchant: boolean // Add merchant status helper
  login: (email: string, password: string) => Promise<void>
  register: (
    name: string, // Simplified to just user's name
    email: string,
    password: string,
  ) => Promise<void>
  registerMerchant: (
    businessName: string,
    ownerName: string,
    email: string,
    phone: string,
    businessType: BusinessType, // Fix type
    mpesaTillNumber: string,
    password: string,
  ) => Promise<void>
  logout: () => void
  loading: boolean
  refreshUser: () => Promise<void> // Add method to refresh user data
}

const AuthContext = createContext<AuthContextType | undefined>(undefined)

export function AuthProvider({ children }: { children: React.ReactNode }) {
  const [user, setUser] = useState<User | null>(null)
  const [loading, setLoading] = useState(true)
  const router = useRouter()

  useEffect(() => {
    console.log("[AuthContext] Checking for existing access token...") // Added log
    const token = localStorage.getItem("accessToken") // Changed from "auth_token" to "accessToken"
    if (token) {
      apiService
        .getMe() // Use apiService.getMe()
        .then((response) => {
          console.log("[AuthContext] User data fetched successfully:", response.email); // Added log
          setUser(response)
        })
        .catch((err) => {
          console.error("[AuthContext] Failed to fetch user data with token:", err); // Added log
          localStorage.removeItem("accessToken") // Changed from "auth_token" to "accessToken"
        })
        .finally(() => {
          setLoading(false)
        })
    } else {
      console.log("[AuthContext] No access token found, user not authenticated."); // Added log
      setLoading(false)
    }
  }, [])

  const login = async (email: string, password: string) => {
    try {
      console.log(`[AuthContext] Attempting to log in user: ${email}`); // Added log
      const response = await apiService.login(email, password) // Use apiService.login()
      localStorage.setItem("accessToken", response.access_token) // Changed from "auth_token" to "accessToken"
      console.log("[AuthContext] Login successful, fetching user details..."); // Added log

      const userData = await apiService.getMe() // Fetch user details after login
      setUser(userData)
      router.push("/dashboard")
    } catch (error) {
      console.error("[AuthContext] Login failed:", error); // Added log
      throw new Error("Invalid credentials")
    }
  }

  const register = async (
    name: string,
    email: string,
    password: string,
  ) => {
    try {
      console.log(`[AuthContext] Attempting to register user: ${email}`); // Added log
      // Only create user account
      await apiService.registerUser(
        email,
        password,
        name,
        undefined, // merchant_id is optional at this stage
      )

      const { access_token } = await apiService.login(email, password); // Log in the user after registration
      localStorage.setItem("accessToken", access_token); // Changed from "auth_token" to "accessToken"
      console.log("[AuthContext] Registration successful, fetching user details..."); // Added log

      const userData = await apiService.getMe(); // Fetch user details after login
      setUser(userData);
      router.push("/dashboard");
    } catch (error) {
      console.error("[AuthContext] Registration error:", error);
      throw new Error("Registration failed");
    }
  }

  const registerMerchant = async (
    businessName: string,
    ownerName: string,
    email: string,
    phone: string,
    businessType: BusinessType, // Fix type
    mpesaTillNumber: string,
    password: string,
  ) => {
    try {
      console.log(`[AuthContext] Attempting to register merchant and user for: ${email}`); // Added log
      // First register the merchant
      const merchantData: MerchantCreateRequest = {
        business_name: businessName,
        owner_name: ownerName,
        email,
        phone,
        business_type: businessType,
        mpesa_till_number: mpesaTillNumber,
      }
      const merchantResponse = await apiService.createMerchant(merchantData)
      console.log("[AuthContext] Merchant registered, ID:", merchantResponse.id); // Added log

      // Then create user account linked to the new merchant
      await apiService.registerUser(
        email,
        password,
        ownerName,
        merchantResponse.id, // Link user to the newly created merchant
      )
      console.log("[AuthContext] User account linked to merchant, attempting login..."); // Added log

      const { access_token } = await apiService.login(email, password); // Log in the user after registration
      localStorage.setItem("accessToken", access_token); // Changed from "auth_token" to "accessToken"

      const userData = await apiService.getMe(); // Fetch user details after login
      setUser(userData);
      router.push("/dashboard");
    } catch (error) {
      console.error("[AuthContext] Merchant registration error:", error);
      throw new Error("Merchant registration failed");
    }
  }

  const refreshUser = async () => {
    try {
      const userData = await apiService.getMe()
      setUser(userData)
    } catch (error) {
      console.error("[AuthContext] Failed to refresh user data:", error)
      // If refresh fails, user might need to login again
      localStorage.removeItem("accessToken")
      setUser(null)
    }
  }

  const logout = () => {
    console.log("[AuthContext] Logging out user."); // Added log
    localStorage.removeItem("accessToken") // Changed from "auth_token" to "accessToken"
    setUser(null)
    router.push("/login")
  }

  // Computed property to check if user is a merchant
  const isMerchant = Boolean(user?.merchant_id)

  return <AuthContext.Provider value={{ 
    user, 
    isMerchant, 
    login, 
    register, 
    registerMerchant, 
    logout, 
    loading, 
    refreshUser 
  }}>{children}</AuthContext.Provider>
}

export function useAuth() {
  const context = useContext(AuthContext)
  if (context === undefined) {
    throw new Error("useAuth must be used within an AuthProvider")
  }
  return context
}