"use client"

import type React from "react"
import { createContext, useContext, useEffect, useState } from "react"
import { useRouter } from "next/navigation"
import api from "@/lib/api"

interface User {
  id: string
  email: string
  name: string
  merchant_id?: string
}

interface AuthContextType {
  user: User | null
  login: (email: string, password: string) => Promise<void>
  register: (name: string, email: string, password: string, businessType: string) => Promise<void>
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
      // Verify token and get user info
      api
        .get("/auth/me")
        .then((response) => {
          setUser(response.data)
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
      const response = await api.post("/auth/login", { email, password })
      const { access_token, user: userData } = response.data

      localStorage.setItem("auth_token", access_token)
      setUser(userData)
      router.push("/dashboard")
    } catch (error) {
      throw new Error("Invalid credentials")
    }
  }

  const register = async (name: string, email: string, password: string, businessType: string) => {
    try {
      // First register the merchant
      const merchantResponse = await api.post("/merchants", {
        name,
        email,
        business_type: businessType,
        phone: "", // Will be updated later
        location: "", // Will be updated later
      })

      // Then create user account (assuming there's an auth endpoint)
      const authResponse = await api.post("/auth/register", {
        email,
        password,
        name,
        merchant_id: merchantResponse.data.id,
      })

      const { access_token, user: userData } = authResponse.data
      localStorage.setItem("auth_token", access_token)
      setUser(userData)
      router.push("/dashboard")
    } catch (error) {
      throw new Error("Registration failed")
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
