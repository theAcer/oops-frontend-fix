"use client"

import type React from "react"

import { useState } from "react"
import { useRouter } from "next/navigation"
import { DashboardLayout } from "@/components/layout/dashboard-layout"
import { CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card"
import { Button } from "@/components/ui/button"
import { Input } from "@/components/ui/input"
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select" // Import Select components
import { useAuth } from "@/contexts/auth-context"
import { apiService } from "@/services/api-service"
import { ArrowLeft } from "lucide-react"
import Link from "next/link"
import { AnimatedButton } from "@/components/animated-button"
import { BlurredCard } from "@/components/blurred-card"

export default function BecomeMerchantPage() {
  const router = useRouter()
  const { user } = useAuth()
  const [formData, setFormData] = useState({
    businessName: "",
    ownerName: user?.name || "",
    email: user?.email || "",
    phone: "",
    businessType: "",
  })
  const [error, setError] = useState("")
  const [loading, setLoading] = useState(false)

  // Redirect if user already has a merchant_id
  if (user && user.merchant_id) {
    router.push("/dashboard");
    return null;
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
      // Create merchant via API
      await apiService.createMerchant({
        business_name: formData.businessName,
        owner_name: formData.ownerName,
        email: formData.email,
        phone: formData.phone,
        business_type: formData.businessType as any, // Cast to BusinessType enum
        mpesa_till_number: "000000", // Temporary placeholder - will be set via channels
      })
      
      router.push("/dashboard/channels")
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

  const handleSelectChange = (name: string, value: string) => {
    setFormData((prev) => ({
      ...prev,
      [name]: value,
    }))
  }

  return (
    <DashboardLayout>
      <div className="space-y-8">
        <div className="flex items-center space-x-4">
          <Link href="/dashboard">
            <Button variant="ghost" size="sm" className="text-muted-foreground hover:bg-accent hover:text-foreground">
              <ArrowLeft className="h-4 w-4 mr-2" />
              Back to Dashboard
            </Button>
          </Link>
        </div>

        <div>
          <h1 className="text-3xl font-bold text-foreground">Become a Merchant</h1>
          <p className="text-muted-foreground mt-1">Register your business to access loyalty features</p>
        </div>

        <BlurredCard>
          <CardHeader>
            <CardTitle className="text-foreground">Business Details</CardTitle>
            <CardDescription className="text-muted-foreground">Provide your business information to get started</CardDescription>
          </CardHeader>
          <CardContent>
            <form onSubmit={handleSubmit} className="space-y-6">
              {error && (
                <div className="p-3 text-sm text-destructive bg-destructive/10 border border-destructive/30 rounded-md">{error}</div>
              )}

              <div className="space-y-2">
                <label htmlFor="businessName" className="text-sm font-medium text-foreground">
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
                  className="bg-background/50 border-border focus:border-primary"
                />
              </div>

              <div className="space-y-2">
                <label htmlFor="ownerName" className="text-sm font-medium text-foreground">
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
                  disabled
                  className="bg-background/50 border-border focus:border-primary disabled:opacity-70 disabled:cursor-not-allowed"
                />
              </div>

              <div className="space-y-2">
                <label htmlFor="email" className="text-sm font-medium text-foreground">
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
                  disabled
                  className="bg-background/50 border-border focus:border-primary disabled:opacity-70 disabled:cursor-not-allowed"
                />
              </div>

              <div className="space-y-2">
                <label htmlFor="phone" className="text-sm font-medium text-foreground">
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
                  className="bg-background/50 border-border focus:border-primary"
                />
              </div>

              <div className="space-y-2">
                <label htmlFor="businessType" className="text-sm font-medium text-foreground">
                  Business Type <span className="text-destructive">*</span>
                </label>
                <select
                  id="businessType"
                  name="businessType"
                  value={formData.businessType}
                  onChange={handleChange}
                  required
                  className="flex h-10 w-full items-center justify-between rounded-md border border-input bg-background px-3 py-2 text-sm ring-offset-background placeholder:text-muted-foreground focus:outline-none focus:ring-2 focus:ring-ring focus:ring-offset-2 disabled:cursor-not-allowed disabled:opacity-50"
                >
                  <option value="">Select business type</option>
                  <option value="retail">Retail</option>
                  <option value="restaurant">Restaurant</option>
                  <option value="service">Service</option>
                  <option value="salon">Salon</option>
                  <option value="other">Other</option>
                </select>
              </div>

              <AnimatedButton type="submit" className="w-full py-2.5 text-lg" disabled={loading}>
                {loading ? "Registering Business..." : "Register My Business"}
              </AnimatedButton>
            </form>
          </CardContent>
        </BlurredCard>
      </div>
    </DashboardLayout>
  )
}