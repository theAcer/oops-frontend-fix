"use client"

import type React from "react"

import { useState } from "react"
import { useRouter } from "next/navigation"
import { DashboardLayout } from "@/components/layout/dashboard-layout"
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card"
import { Button } from "@/components/ui/button"
import { Input } from "@/components/ui/input"
import { Badge } from "@/components/ui/badge"
import { apiService } from "@/services/api-service"
import { useAuth } from "@/contexts/auth-context"
import { ArrowLeft, Save, Send } from "lucide-react"
import Link from "next/link"
import { AnimatedButton } from "@/components/animated-button" // Import AnimatedButton

export default function CreateCampaignPage() {
  const router = useRouter()
  const { user } = useAuth()
  const [loading, setLoading] = useState(false)
  const [formData, setFormData] = useState({
    name: "",
    description: "",
    campaign_type: "sms",
    target_audience: "all_customers",
    budget: 0,
    start_date: "",
    end_date: "",
    message: "",
  })

  const handleSubmit = async (e: React.FormEvent, launch = false) => {
    e.preventDefault()
    if (!user?.merchant_id) return

    setLoading(true)
    try {
      const campaignData = {
        ...formData,
        merchant_id: user.merchant_id,
        status: launch ? "active" : "draft",
      }

      const campaign = await apiService.createCampaign(campaignData)

      if (launch) {
        await apiService.launchCampaign(campaign.id)
      }

      router.push("/dashboard/campaigns")
    } catch (error) {
      console.error("Failed to create campaign:", error)
    } finally {
      setLoading(false)
    }
  }

  const handleChange = (e: React.ChangeEvent<HTMLInputElement | HTMLSelectElement | HTMLTextAreaElement>) => {
    const { name, value } = e.target
    setFormData((prev) => ({
      ...prev,
      [name]: name === "budget" ? Number.parseFloat(value) || 0 : value,
    }))
  }

  return (
    <DashboardLayout>
      <div className="space-y-6">
        <div className="flex items-center space-x-4">
          <Link href="/dashboard/campaigns">
            <Button variant="ghost" size="sm">
              <ArrowLeft className="h-4 w-4 mr-2" />
              Back to Campaigns
            </Button>
          </Link>
        </div>

        <div>
          <h1 className="text-3xl font-bold text-gray-900">Create New Campaign</h1>
          <p className="text-gray-600">Design and launch your marketing campaign</p>
        </div>

        <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
          <div className="lg:col-span-2">
            <Card>
              <CardHeader>
                <CardTitle>Campaign Details</CardTitle>
                <CardDescription>Configure your campaign settings and content</CardDescription>
              </CardHeader>
              <CardContent>
                <form className="space-y-6">
                  <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                    <div className="space-y-2">
                      <label htmlFor="name" className="text-sm font-medium">
                        Campaign Name
                      </label>
                      <Input
                        id="name"
                        name="name"
                        value={formData.name}
                        onChange={handleChange}
                        placeholder="Enter campaign name"
                        required
                      />
                    </div>

                    <div className="space-y-2">
                      <label htmlFor="campaign_type" className="text-sm font-medium">
                        Campaign Type
                      </label>
                      <select
                        id="campaign_type"
                        name="campaign_type"
                        value={formData.campaign_type}
                        onChange={handleChange}
                        className="flex h-10 w-full rounded-md border border-input bg-background px-3 py-2 text-sm ring-offset-background focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring focus-visible:ring-offset-2"
                      >
                        <option value="sms">SMS Campaign</option>
                        <option value="email">Email Campaign</option>
                        <option value="loyalty">Loyalty Campaign</option>
                        <option value="retention">Retention Campaign</option>
                      </select>
                    </div>
                  </div>

                  <div className="space-y-2">
                    <label htmlFor="description" className="text-sm font-medium">
                      Description
                    </label>
                    <textarea
                      id="description"
                      name="description"
                      value={formData.description}
                      onChange={handleChange}
                      placeholder="Describe your campaign objectives"
                      rows={3}
                      className="flex w-full rounded-md border border-input bg-background px-3 py-2 text-sm ring-offset-background focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring focus-visible:ring-offset-2"
                    />
                  </div>

                  <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                    <div className="space-y-2">
                      <label htmlFor="target_audience" className="text-sm font-medium">
                        Target Audience
                      </label>
                      <select
                        id="target_audience"
                        name="target_audience"
                        value={formData.target_audience}
                        onChange={handleChange}
                        className="flex h-10 w-full rounded-md border border-input bg-background px-3 py-2 text-sm ring-offset-background focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring focus-visible:ring-offset-2"
                      >
                        <option value="all_customers">All Customers</option>
                        <option value="vip_customers">VIP Customers</option>
                        <option value="new_customers">New Customers</option>
                        <option value="inactive_customers">Inactive Customers</option>
                        <option value="high_spenders">High Spenders</option>
                      </select>
                    </div>

                    <div className="space-y-2">
                      <label htmlFor="budget" className="text-sm font-medium">
                        Budget (KES)
                      </label>
                      <Input
                        id="budget"
                        name="budget"
                        type="number"
                        value={formData.budget}
                        onChange={handleChange}
                        placeholder="0"
                        min="0"
                        step="100"
                      />
                    </div>
                  </div>

                  <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                    <div className="space-y-2">
                      <label htmlFor="start_date" className="text-sm font-medium">
                        Start Date
                      </label>
                      <Input
                        id="start_date"
                        name="start_date"
                        type="datetime-local"
                        value={formData.start_date}
                        onChange={handleChange}
                        required
                      />
                    </div>

                    <div className="space-y-2">
                      <label htmlFor="end_date" className="text-sm font-medium">
                        End Date
                      </label>
                      <Input
                        id="end_date"
                        name="end_date"
                        type="datetime-local"
                        value={formData.end_date}
                        onChange={handleChange}
                        required
                      />
                    </div>
                  </div>

                  <div className="space-y-2">
                    <label htmlFor="message" className="text-sm font-medium">
                      Campaign Message
                    </label>
                    <textarea
                      id="message"
                      name="message"
                      value={formData.message}
                      onChange={handleChange}
                      placeholder="Enter your campaign message..."
                      rows={4}
                      className="flex w-full rounded-md border border-input bg-background px-3 py-2 text-sm ring-offset-background focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring focus-visible:ring-offset-2"
                    />
                    <p className="text-xs text-gray-500">{formData.message.length}/160 characters (SMS limit)</p>
                  </div>

                  <div className="flex space-x-4">
                    <Button
                      type="button"
                      variant="outline"
                      onClick={(e) => handleSubmit(e, false)}
                      disabled={loading}
                      className="bg-transparent"
                    >
                      <Save className="h-4 w-4 mr-2" />
                      Save as Draft
                    </Button>
                    <AnimatedButton type="button" onClick={(e) => handleSubmit(e, true)} disabled={loading}>
                      <Send className="h-4 w-4 mr-2" />
                      {loading ? "Creating..." : "Create & Launch"}
                    </AnimatedButton>
                  </div>
                </form>
              </CardContent>
            </Card>
          </div>

          <div className="space-y-6">
            <Card>
              <CardHeader>
                <CardTitle>Campaign Preview</CardTitle>
                <CardDescription>How your campaign will appear</CardDescription>
              </CardHeader>
              <CardContent>
                <div className="space-y-4">
                  <div>
                    <p className="text-sm font-medium">Campaign Name</p>
                    <p className="text-sm text-gray-600">{formData.name || "Untitled Campaign"}</p>
                  </div>

                  <div>
                    <p className="text-sm font-medium">Type</p>
                    <Badge variant="outline">{formData.campaign_type}</Badge>
                  </div>

                  <div>
                    <p className="text-sm font-medium">Target</p>
                    <p className="text-sm text-gray-600">{formData.target_audience.replace("_", " ")}</p>
                  </div>

                  {formData.message && (
                    <div>
                      <p className="text-sm font-medium">Message Preview</p>
                      <div className="p-3 bg-gray-50 rounded-lg border">
                        <p className="text-sm">{formData.message}</p>
                      </div>
                    </div>
                  )}
                </div>
              </CardContent>
            </Card>

            <Card>
              <CardHeader>
                <CardTitle>Campaign Tips</CardTitle>
              </CardHeader>
              <CardContent>
                <div className="space-y-3 text-sm">
                  <div className="flex items-start space-x-2">
                    <div className="w-2 h-2 bg-blue-500 rounded-full mt-1.5"></div>
                    <p>Keep SMS messages under 160 characters for best delivery rates</p>
                  </div>
                  <div className="flex items-start space-x-2">
                    <div className="w-2 h-2 bg-green-500 rounded-full mt-1.5"></div>
                    <p>Personalize messages with customer names for higher engagement</p>
                  </div>
                  <div className="flex items-start space-x-2">
                    <div className="w-2 h-2 bg-purple-500 rounded-full mt-1.5"></div>
                    <p>Schedule campaigns during peak customer activity hours</p>
                  </div>
                </div>
              </CardContent>
            </Card>
          </div>
        </div>
      </div>
    </DashboardLayout>
  )
}