"use client"

import React, { useState, useEffect } from "react"
import { useRouter } from "next/navigation"
import { DashboardLayout } from "@/components/layout/dashboard-layout"
import { CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card"
import { Button } from "@/components/ui/button"
import { Input } from "@/components/ui/input"
import { useAuth } from "@/contexts/auth-context"
import { apiService } from "@/services/api-service"
import { ArrowLeft, Save } from "lucide-react"
import Link from "next/link"
import { AnimatedButton } from "@/components/animated-button"
import { BlurredCard } from "@/components/blurred-card"
import { useMerchant } from "@/hooks/use-api"

export default function DarajaIntegrationPage() {
  const _router = useRouter() // Renamed to _router to ignore unused var warning
  const { user } = useAuth()
  const { data: merchant, isLoading: merchantLoading, error: merchantError, mutate: refreshMerchant } = useMerchant()

  const [formData, setFormData] = useState({
    daraja_consumer_key: "",
    daraja_consumer_secret: "",
    daraja_shortcode: "",
    daraja_passkey: "",
  })
  const [error, setError] = useState("")
  const [loading, setLoading] = useState(false)
  const [successMessage, setSuccessMessage] = useState("")

  useEffect(() => {
    if (merchant) {
      setFormData({
        daraja_consumer_key: merchant.daraja_consumer_key || "",
        daraja_consumer_secret: merchant.daraja_consumer_secret || "",
        daraja_shortcode: merchant.daraja_shortcode || "",
        daraja_passkey: merchant.daraja_passkey || "",
      })
    }
  }, [merchant])

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    setError("")
    setSuccessMessage("")

    if (!user?.merchant_id) {
      setError("You must be linked to a merchant to configure Daraja integration.")
      return
    }

    setLoading(true)
    try {
      await apiService.updateMerchant(user.merchant_id, {
        daraja_consumer_key: formData.daraja_consumer_key,
        daraja_consumer_secret: formData.daraja_consumer_secret,
        daraja_shortcode: formData.daraja_shortcode,
        daraja_passkey: formData.daraja_passkey,
      })
      setSuccessMessage("Daraja API credentials saved successfully!")
      refreshMerchant()
    } catch (err: any) {
      console.error("Failed to save Daraja credentials:", err)
      setError(err.response?.data?.detail || "Failed to save Daraja credentials. Please try again.")
    } finally {
      setLoading(false)
    }
  }

  const handleChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const { name, value } = e.target
    setFormData((prev) => ({
      ...prev,
      [name]: value,
    }))
  }

  if (merchantLoading) {
    return (
      <DashboardLayout>
        <div className="flex items-center justify-center h-64">
          <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-primary"></div>
        </div>
      </DashboardLayout>
    )
  }

  if (merchantError || !user?.merchant_id) {
    return (
      <DashboardLayout>
        <div className="flex items-center justify-center h-64">
          <p className="text-destructive">Error loading merchant data or no merchant linked.</p>
        </div>
      </DashboardLayout>
    )
  }

  return (
    <DashboardLayout>
      <div className="space-y-8">
        <div className="flex items-center space-x-4">
          <Link href="/dashboard/settings">
            <Button variant="ghost" size="sm" className="text-muted-foreground hover:bg-accent hover:text-foreground">
              <ArrowLeft className="h-4 w-4 mr-2" />
              Back to Settings
            </Button>
          </Link>
        </div>

        <div>
          <h1 className="text-3xl font-bold text-foreground">Daraja API Integration</h1>
          <p className="text-muted-foreground mt-1">Configure your M-Pesa Daraja API credentials for real-time transactions.</p>
        </div>

        <BlurredCard>
          <CardHeader>
            <CardTitle className="text-foreground">Daraja API Credentials</CardTitle>
            <CardDescription className="text-muted-foreground">Enter your Safaricom Daraja API keys and shortcodes.</CardDescription>
          </CardHeader>
          <CardContent>
            <form onSubmit={handleSubmit} className="space-y-6">
              {error && (
                <div className="p-3 text-sm text-destructive bg-destructive/10 border border-destructive/30 rounded-md">{error}</div>
              )}
              {successMessage && (
                <div className="p-3 text-sm text-success bg-success/10 border border-success/30 rounded-md">{successMessage}</div>
              )}

              <div className="space-y-2">
                <label htmlFor="daraja_consumer_key" className="text-sm font-medium text-foreground">
                  Consumer Key
                </label>
                <Input
                  id="daraja_consumer_key"
                  name="daraja_consumer_key"
                  type="text"
                  value={formData.daraja_consumer_key}
                  onChange={handleChange}
                  required
                  placeholder="Enter your Daraja Consumer Key"
                  className="bg-background/50 border-border focus:border-primary"
                />
              </div>

              <div className="space-y-2">
                <label htmlFor="daraja_consumer_secret" className="text-sm font-medium text-foreground">
                  Consumer Secret
                </label>
                <Input
                  id="daraja_consumer_secret"
                  name="daraja_consumer_secret"
                  type="password"
                  value={formData.daraja_consumer_secret}
                  onChange={handleChange}
                  required
                  placeholder="Enter your Daraja Consumer Secret"
                  className="bg-background/50 border-border focus:border-primary"
                />
              </div>

              <div className="space-y-2">
                <label htmlFor="daraja_shortcode" className="text-sm font-medium text-foreground">
                  Shortcode (Paybill/Till Number)
                </label>
                <Input
                  id="daraja_shortcode"
                  name="daraja_shortcode"
                  type="text"
                  value={formData.daraja_shortcode}
                  onChange={handleChange}
                  required
                  placeholder="Enter your Daraja Shortcode (e.g., 174379)"
                  className="bg-background/50 border-border focus:border-primary"
                />
              </div>

              <div className="space-y-2">
                <label htmlFor="daraja_passkey" className="text-sm font-medium text-foreground">
                  Lipa Na M-Pesa Online Passkey
                </label>
                <Input
                  id="daraja_passkey"
                  name="daraja_passkey"
                  type="password"
                  value={formData.daraja_passkey}
                  onChange={handleChange}
                  required
                  placeholder="Enter your Lipa Na M-Pesa Online Passkey"
                  className="bg-background/50 border-border focus:border-primary"
                />
              </div>

              <AnimatedButton type="submit" className="w-full py-2.5 text-lg" disabled={loading}>
                <Save className="h-4 w-4 mr-2" />
                {loading ? "Saving..." : "Save Credentials"}
              </AnimatedButton>
            </form>
          </CardContent>
        </BlurredCard>

        <BlurredCard>
          <CardHeader>
            <CardTitle className="text-foreground">Important Notes</CardTitle>
          </CardHeader>
          <CardContent>
            <ul className="list-disc list-inside space-y-2 text-sm text-muted-foreground">
              <li>Ensure your Daraja API credentials are correct to enable transaction syncing.</li>
              <li>Your M-Pesa Till Number (configured during merchant registration) will be used for transactions.</li>
              <li>For security, Daraja API keys are sensitive. Do not share them publicly.</li>
              <li>Contact Safaricom support if you need help retrieving your Daraja API credentials.</li>
            </ul>
          </CardContent>
        </BlurredCard>
      </div>
    </DashboardLayout>
  )
}