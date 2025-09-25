"use client"

import type React from "react"
import { useState } from "react"
import { useRouter } from "next/navigation"
import { DashboardLayout } from "@/components/layout/dashboard-layout"
import { CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card"
import { Button } from "@/components/ui/button"
import { Input } from "@/components/ui/input"
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select"
import { ArrowLeft, Save, TestTube } from "lucide-react"
import Link from "next/link"
import { AnimatedButton } from "@/components/animated-button"
import { BlurredCard } from "@/components/blurred-card"
import { apiService } from "@/services/api-service"
import { toast } from "react-hot-toast"

export default function AddChannelPage() {
  const router = useRouter()
  const [formData, setFormData] = useState({
    name: "",
    type: "",
    shortcode: "",
    environment: "sandbox",
    consumerKey: "",
    consumerSecret: "",
  })
  const [error, setError] = useState("")
  const [loading, setLoading] = useState(false)

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    setError("")

    // Basic validation
    if (!formData.name.trim()) {
      setError("Channel name is required")
      return
    }
    if (!formData.type) {
      setError("Channel type is required")
      return
    }
    if (!formData.shortcode.trim()) {
      setError("Shortcode is required")
      return
    }
    if (!formData.consumerKey.trim()) {
      setError("Consumer key is required")
      return
    }
    if (!formData.consumerSecret.trim()) {
      setError("Consumer secret is required")
      return
    }

    setLoading(true)

    try {
      // Create channel using API
      console.log("Creating channel:", formData)
      
      const channelData = {
        name: formData.name,
        channel_type: formData.type.toLowerCase(),
        shortcode: formData.shortcode,
        environment: formData.environment,
        consumer_key: formData.consumerKey,
        consumer_secret: formData.consumerSecret,
        merchant_id: 1, // Temporary: hardcode merchant_id for testing
      }

      await apiService.createChannel(channelData)
      
      toast.success("Channel created successfully!")
      
      // Redirect to channels list
      router.push("/dashboard/channels")
    } catch (err: any) {
      console.error("Failed to create channel:", err)
      setError(err.response?.data?.detail || "Failed to create channel. Please try again.")
    } finally {
      setLoading(false)
    }
  }

  const handleSelectChange = (name: string, value: string) => {
    console.log(`Updating ${name} to:`, value)
    setFormData((prev) => ({
      ...prev,
      [name]: value,
    }))
    setError("") // Clear error when user makes changes
  }

  const handleInputChange = (e: React.ChangeEvent<HTMLInputElement | HTMLSelectElement>) => {
    const { name, value } = e.target
    setFormData((prev) => ({
      ...prev,
      [name]: value,
    }))
    setError("") // Clear error when user makes changes
  }

  return (
    <DashboardLayout>
      <div className="space-y-8">
        <div className="flex items-center space-x-4">
          <Link href="/dashboard/channels">
            <Button variant="ghost" size="sm" className="text-muted-foreground hover:bg-accent hover:text-foreground">
              <ArrowLeft className="h-4 w-4 mr-2" />
              Back to Channels
            </Button>
          </Link>
          <div>
            <h1 className="text-3xl font-bold text-foreground">Add M-Pesa Channel</h1>
            <p className="text-muted-foreground mt-1">Configure a new M-Pesa payment channel</p>
          </div>
        </div>

        <BlurredCard>
          <CardHeader>
            <CardTitle className="text-foreground">Channel Configuration</CardTitle>
            <CardDescription className="text-muted-foreground">
              Set up your M-Pesa channel details for payment processing
            </CardDescription>
          </CardHeader>
          <CardContent>
            <form onSubmit={handleSubmit} className="space-y-6">
              {error && (
                <div className="p-3 text-sm text-destructive bg-destructive/10 border border-destructive/30 rounded-md">
                  {error}
                </div>
              )}

              <div className="space-y-2">
                <label htmlFor="name" className="text-sm font-medium text-foreground">
                  Channel Name <span className="text-destructive">*</span>
                </label>
                <Input
                  id="name"
                  name="name"
                  type="text"
                  value={formData.name}
                  onChange={handleInputChange}
                  required
                  placeholder="e.g., Main PayBill Channel"
                  className="bg-background/50 border-border focus:border-primary"
                />
              </div>

              <div className="space-y-2">
                <label htmlFor="type" className="text-sm font-medium text-foreground">
                  Channel Type <span className="text-destructive">*</span>
                </label>
                <select
                  id="type"
                  name="type"
                  value={formData.type}
                  onChange={handleInputChange}
                  required
                  className="flex h-10 w-full items-center justify-between rounded-md border border-input bg-background px-3 py-2 text-sm ring-offset-background placeholder:text-muted-foreground focus:outline-none focus:ring-2 focus:ring-ring focus:ring-offset-2 disabled:cursor-not-allowed disabled:opacity-50"
                >
                  <option value="">Select channel type</option>
                  <option value="PayBill">PayBill</option>
                  <option value="Till">Till Number</option>
                  <option value="BuyGoods">Buy Goods (Till Number)</option>
                  <option value="STKPush">STK Push</option>
                </select>
                {formData.type && (
                  <p className="text-xs text-muted-foreground">
                    Selected: <span className="font-medium">{formData.type}</span>
                  </p>
                )}
              </div>

              <div className="space-y-2">
                <label htmlFor="shortcode" className="text-sm font-medium text-foreground">
                  Shortcode <span className="text-destructive">*</span>
                </label>
                <Input
                  id="shortcode"
                  name="shortcode"
                  type="text"
                  value={formData.shortcode}
                  onChange={handleInputChange}
                  required
                  placeholder="e.g., 174379"
                  className="bg-background/50 border-border focus:border-primary"
                />
              </div>

              <div className="space-y-2">
                <label htmlFor="environment" className="text-sm font-medium text-foreground">
                  Environment <span className="text-destructive">*</span>
                </label>
                <select
                  id="environment"
                  name="environment"
                  value={formData.environment}
                  onChange={handleInputChange}
                  required
                  className="flex h-10 w-full items-center justify-between rounded-md border border-input bg-background px-3 py-2 text-sm ring-offset-background placeholder:text-muted-foreground focus:outline-none focus:ring-2 focus:ring-ring focus:ring-offset-2 disabled:cursor-not-allowed disabled:opacity-50"
                >
                  <option value="">Select environment</option>
                  <option value="sandbox">Sandbox (Testing)</option>
                  <option value="production">Production (Live)</option>
                </select>
                {formData.environment && (
                  <p className="text-xs text-muted-foreground">
                    Environment: <span className="font-medium">{formData.environment}</span>
                  </p>
                )}
              </div>

              <div className="space-y-2">
                <label htmlFor="consumerKey" className="text-sm font-medium text-foreground">
                  Consumer Key <span className="text-destructive">*</span>
                </label>
                <Input
                  id="consumerKey"
                  name="consumerKey"
                  type="text"
                  value={formData.consumerKey}
                  onChange={handleInputChange}
                  required
                  placeholder="Your Daraja Consumer Key"
                  className="bg-background/50 border-border focus:border-primary"
                />
              </div>

              <div className="space-y-2">
                <label htmlFor="consumerSecret" className="text-sm font-medium text-foreground">
                  Consumer Secret <span className="text-destructive">*</span>
                </label>
                <Input
                  id="consumerSecret"
                  name="consumerSecret"
                  type="password"
                  value={formData.consumerSecret}
                  onChange={handleInputChange}
                  required
                  placeholder="Your Daraja Consumer Secret"
                  className="bg-background/50 border-border focus:border-primary"
                />
              </div>

              <div className="bg-muted/30 p-4 rounded-lg">
                <div className="flex items-start space-x-3">
                  <TestTube className="h-5 w-5 text-blue-500 mt-0.5" />
                  <div>
                    <h4 className="font-medium text-foreground">Sandbox Environment</h4>
                    <p className="text-sm text-muted-foreground mt-1">
                      Using sandbox environment allows you to test your integration without processing real payments.
                      Get your sandbox credentials from the Safaricom Developer Portal.
                    </p>
                  </div>
                </div>
              </div>

              <div className="flex space-x-4">
                <AnimatedButton
                  type="submit"
                  className="flex-1"
                  disabled={loading || !formData.name || !formData.type || !formData.shortcode || !formData.consumerKey || !formData.consumerSecret}
                >
                  <Save className="h-4 w-4 mr-2" />
                  {loading ? "Creating Channel..." : "Create Channel"}
                </AnimatedButton>
                <Button
                  type="button"
                  variant="outline"
                  onClick={() => router.push("/dashboard/channels")}
                  disabled={loading}
                >
                  Cancel
                </Button>
              </div>
            </form>
          </CardContent>
        </BlurredCard>
      </div>
    </DashboardLayout>
  )
}
