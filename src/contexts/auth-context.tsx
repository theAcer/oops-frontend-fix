"use client"

import type React from "react"
import { createContext, useContext, useEffect, useState } from "react"
import { useRouter } from "next/navigation"
import { apiService } from "@/services/api-service" // Import apiService

interface User {
  id: string
  email: string
  name: string
  merchant_id?: string
}

interface AuthContextType {
  user: User | null
  login: (email: string, password: string) => Promise<void>
  register: (
    businessName: string,
    ownerName: string,
    email: string,
    phone: string,
    businessType: string,
    mpesaTillNumber: string,
    password: string,
  ) => Promise<void>
  logout: () => void
  loading: boolean
}

const AuthContext = createContext<AuthContextType | undefined>(undefined)

export function AuthProvider({ children }: { children: React.ReactNode }) {
  const [user, setUser] = useState<User | null>(null)
  const [loading, setLoading] = useState(true)
  const router = useRouter()

  useEffect(() => {
    const token = localStorage.getItem("auth_token")
    if (token) {
      apiService
        .getMe() // Use apiService.getMe()
        .then((response) => {
          setUser(response)
        })
        .catch(() => {
          localStorage.removeItem("auth_token")
        })
        .finally(() => {
          setLoading(false)
        })
    } else {
      setLoading(false)
    }
  }, [])

  const login = async (email: string, password: string) => {
    try {
      const response = await apiService.login(email, password) // Use apiService.login()
      localStorage.setItem("auth_token", response.access_token)

      const userData = await apiService.getMe() // Fetch user details after login
      setUser(userData)
      router.push("/dashboard")
    } catch (error) {
      throw new Error("Invalid credentials")
    }
  }

  const register = async (
    businessName: string,
    ownerName: string,
    email: string,
    phone: string,
    businessType: string,
    mpesaTillNumber: string,
    password: string,
  ) => {
    try {
      // First register the merchant
      const merchantResponse = await apiService.createMerchant({
        business_name: businessName,
        owner_name: ownerName,
        email,
        phone,
        business_type: businessType,
        mpesa_till_number: mpesaTillNumber,
      })

      // Then create user account
      const authResponse = await apiService.registerUser(
        email,
        password,
        ownerName, // Using ownerName for the user's name
        merchantResponse.id,
      )

      const { access_token } = await apiService.login(email, password); // Log in the user after registration
      localStorage.setItem("auth_token", access_token);

      const userData = await apiService.getMe(); // Fetch user details after login
      setUser(userData);
      router.push("/dashboard");
    } catch (error) {
      console.error("Registration error:", error);
      throw new Error("Registration failed");
    }
  }

  const logout = () => {
    localStorage.removeItem("auth_token")
    setUser(null)
    router.push("/login")
  }

  return <AuthContext.Provider value={{ user, login, register, logout, loading }}>{children}</AuthContext.Provider>
}

export function useAuth() {
  const context = useContext(AuthContext)
  if (context === undefined) {
    throw new Error("useAuth must be used within an AuthProvider")
  }
  return context
}