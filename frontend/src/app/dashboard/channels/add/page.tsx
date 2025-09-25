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
    setLoading(true)

    try {
      // TODO: Implement API call to create channel
      console.log("Creating channel:", formData)

      // For now, just redirect to channels list
      router.push("/dashboard/channels")
    } catch (err: any) {
      console.error("Failed to create channel:", err)
      setError(err.response?.data?.detail || "Failed to create channel. Please try again.")
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
                  Channel Name
                </label>
                <Input
                  id="name"
                  name="name"
                  type="text"
                  value={formData.name}
                  onChange={handleChange}
                  required
                  placeholder="e.g., Main PayBill Channel"
                  className="bg-background/50 border-border focus:border-primary"
                />
              </div>

              <div className="space-y-2">
                <label htmlFor="type" className="text-sm font-medium text-foreground">
                  Channel Type
                </label>
                <Select onValueChange={(value) => handleSelectChange("type", value)} value={formData.type} required>
                  <SelectTrigger className="w-full bg-background/50 border-border focus:border-primary">
                    <SelectValue placeholder="Select channel type" />
                  </SelectTrigger>
                  <SelectContent>
                    <SelectItem value="PayBill">PayBill</SelectItem>
                    <SelectItem value="BuyGoods">Buy Goods (Till Number)</SelectItem>
                    <SelectItem value="STKPush">STK Push</SelectItem>
                  </SelectContent>
                </Select>
              </div>

              <div className="space-y-2">
                <label htmlFor="shortcode" className="text-sm font-medium text-foreground">
                  Shortcode
                </label>
                <Input
                  id="shortcode"
                  name="shortcode"
                  type="text"
                  value={formData.shortcode}
                  onChange={handleChange}
                  required
                  placeholder="e.g., 174379"
                  className="bg-background/50 border-border focus:border-primary"
                />
              </div>

              <div className="space-y-2">
                <label htmlFor="environment" className="text-sm font-medium text-foreground">
                  Environment
                </label>
                <Select onValueChange={(value) => handleSelectChange("environment", value)} value={formData.environment} required>
                  <SelectTrigger className="w-full bg-background/50 border-border focus:border-primary">
                    <SelectValue />
                  </SelectTrigger>
                  <SelectContent>
                    <SelectItem value="sandbox">Sandbox (Testing)</SelectItem>
                    <SelectItem value="production">Production (Live)</SelectItem>
                  </SelectContent>
                </Select>
              </div>

              <div className="space-y-2">
                <label htmlFor="consumerKey" className="text-sm font-medium text-foreground">
                  Consumer Key
                </label>
                <Input
                  id="consumerKey"
                  name="consumerKey"
                  type="text"
                  value={formData.consumerKey}
                  onChange={handleChange}
                  required
                  placeholder="Your Daraja Consumer Key"
                  className="bg-background/50 border-border focus:border-primary"
                />
              </div>

              <div className="space-y-2">
                <label htmlFor="consumerSecret" className="text-sm font-medium text-foreground">
                  Consumer Secret
                </label>
                <Input
                  id="consumerSecret"
                  name="consumerSecret"
                  type="password"
                  value={formData.consumerSecret}
                  onChange={handleChange}
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
                <AnimatedButton type="submit" className="flex-1" disabled={loading}>
                  <Save className="h-4 w-4 mr-2" />
                  {loading ? "Creating Channel..." : "Create Channel"}
                </AnimatedButton>
                <Button type="button" variant="outline" onClick={() => router.push("/dashboard/channels")}>
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
