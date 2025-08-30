"use client"

import type React from "react"

import { useState } from "react"
import { useRouter } from "next/navigation"
import { DashboardLayout } from "@/components/layout/dashboard-layout"
import { CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card" // Keep Card parts for structure
import { Button } from "@/components/ui/button"
import { Input } from "@/components/ui/input"
import { useAuth } from "@/contexts/auth-context"
import { apiService } from "@/services/api-service"
import { ArrowLeft, Save } from "lucide-react"
import Link from "next/link"
import { AnimatedButton } from "@/components/animated-button" // Import AnimatedButton
import { BlurredCard } from "@/components/blurred-card" // Import BlurredCard

export default function BecomeMerchantPage() {
  const router = useRouter()
  const { user, logout } = useAuth() // Get user and logout from auth context
  const [formData, setFormData] = useState({
    businessName: "",
    ownerName: user?.name || "", // Pre-fill with user's name
    email: user?.email || "", // Pre-fill with user's email
    phone: "",
    businessType: "",
    mpesaTillNumber: "",
  })
  const [error, setError] = useState("")
  const [loading, setLoading] = useState(false)

  // Redirect if user already has a merchant_id
  if (user && user.merchant_id) {
    router.push("/dashboard");
    return null; // Or show a message that they are already a merchant
  }

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    setError("")

    if (!user) {
      setError("You must be logged in to register a merchant.")
      return
    }

    setLoading(true)
    try {
      await apiService.linkUserToMerchant({
        business_name: formData.businessName,
        owner_name: formData.ownerName,
        email: formData.email,
        phone: formData.phone,
        business_type: formData.businessType,
        mpesa_till_number: formData.mpesaTillNumber,
      })
      
      // After successful merchant creation and linking, refresh user data
      // A simple way is to log out and log back in, or refetch user data
      // For now, let's just redirect to dashboard and rely on next page load to refresh user
      router.push("/dashboard")
    } catch (err: any) {
      console.error("Failed to register merchant:", err)
      setError(err.response?.data?.detail || "Failed to register merchant. Please try again.")
    } finally {
      setLoading(false)
    }
  }

  const handleChange = (e: React.ChangeEvent<HTMLInputElement | HTMLSelectElement>) => {
    const { name, value } = e.target
    setFormData((prev) => ({
      ...prev,
      [name]: value,
    }))
  }

  return (
    <DashboardLayout>
      <div className="space-y-6">
        <div className="flex items-center space-x-4">
          <Link href="/dashboard">
            <Button variant="ghost" size="sm">
              <ArrowLeft className="h-4 w-4 mr-2" />
              Back to Dashboard
            </Button>
          </Link>
        </div>

        <div>
          <h1 className="text-3xl font-bold text-gray-900">Become a Merchant</h1>
          <p className="text-gray-600">Register your business to access loyalty features</p>
        </div>

        <BlurredCard>
          <CardHeader>
            <CardTitle>Business Details</CardTitle>
            <CardDescription>Provide your business information to get started</CardDescription>
          </CardHeader>
          <CardContent>
            <form onSubmit={handleSubmit} className="space-y-6">
              {error && (
                <div className="p-3 text-sm text-red-600 bg-red-50 border border-red-200 rounded-md">{error}</div>
              )}

              <div className="space-y-2">
                <label htmlFor="businessName" className="text-sm font-medium">
                  Business Name
                </label>
                <Input
                  id="businessName"
                  name="businessName"
                  type="text"
                  value={formData.businessName}
                  onChange={handleChange}
                  required
                  placeholder="e.g., My Awesome Shop"
                />
              </div>

              <div className="space-y-2">
                <label htmlFor="ownerName" className="text-sm font-medium">
                  Owner Name
                </label>
                <Input
                  id="ownerName"
                  name="ownerName"
                  type="text"
                  value={formData.ownerName}
                  onChange={handleChange}
                  required
                  placeholder="Your full name"
                  disabled // Owner name is pre-filled from user data
                />
              </div>

              <div className="space-y-2">
                <label htmlFor="email" className="text-sm font-medium">
                  Business Email
                </label>
                <Input
                  id="email"
                  name="email"
                  type="email"
                  value={formData.email}
                  onChange={handleChange}
                  required
                  placeholder="business@example.com"
                  disabled // Email is pre-filled from user data
                />
              </div>

              <div className="space-y-2">
                <label htmlFor="phone" className="text-sm font-medium">
                  Business Phone Number
                </label>
                <Input
                  id="phone"
                  name="phone"
                  type="tel"
                  value={formData.phone}
                  onChange={handleChange}
                  required
                  placeholder="e.g., 254712345678"
                />
              </div>

              <div className="space-y-2">
                <label htmlFor="businessType" className="text-sm font-medium">
                  Business Type
                </label>
                <select
                  id="businessType"
                  name="businessType"
                  value={formData.businessType}
                  onChange={handleChange}
                  required
                  className="flex h-10 w-full rounded-md border border-input bg-background px-3 py-2 text-sm ring-offset-background focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring focus-visible:ring-offset-2"
                >
                  <option value="">Select business type</option>
                  <option value="retail">Retail</option>
                  <option value="restaurant">Restaurant</option>
                  <option value="service">Service</option>
                  <option value="ecommerce">E-commerce</option>
                  <option value="other">Other</option>
                </select>
              </div>

              <div className="space-y-2">
                <label htmlFor="mpesaTillNumber" className="text-sm font-medium">
                  M-Pesa Till Number
                </label>
                <Input
                  id="mpesaTillNumber"
                  name="mpesaTillNumber"
                  type="text"
                  value={formData.mpesaTillNumber}
                  onChange={handleChange}
                  required
                  placeholder="Enter your M-Pesa Till Number"
                />
              </div>

              <AnimatedButton type="submit" className="w-full" disabled={loading}>
                {loading ? "Registering Business..." : "Register My Business"}
              </AnimatedButton>
            </form>
          </CardContent>
        </BlurredCard>
      </div>
    </DashboardLayout>
  )
}