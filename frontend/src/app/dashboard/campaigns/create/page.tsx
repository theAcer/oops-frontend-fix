"use client"

import type React from "react"

import { useState } from "react"
import { useRouter } from "next/navigation"
import { DashboardLayout } from "@/components/layout/dashboard-layout"
import { CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card"
import { Button } from "@/components/ui/button"
import { Badge } from "@/components/ui/badge"
import { Textarea } from "@/components/ui/textarea"
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select"
import { apiService } from "@/services/api-service"
import { useAuth } from "@/contexts/auth-context"
import { ArrowLeft, Save, Send } from "lucide-react"
import Link from "next/link"
import { AnimatedButton } from "@/components/animated-button"
import { BlurredCard } from "@/components/blurred-card"
import { Input } from "@/components/ui/input" // Import Input component

export default function CreateCampaignPage() {
  const router = useRouter()
  const { user } = useAuth()
  const [loading, setLoading] = useState(false)
  const [formData, setFormData] = useState({
    name: "",
    description: "",
    campaign_type: "discount", // Changed default to discount as per backend enum
    target_audience: "all_customers",
    budget: 0,
    start_date: "",
    end_date: "",
    sms_message: "", // Changed from 'message' to 'sms_message' to match backend schema
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
        // Ensure dates are in ISO format if backend expects it
        start_date: formData.start_date ? new Date(formData.start_date).toISOString() : undefined,
        end_date: formData.end_date ? new Date(formData.end_date).toISOString() : undefined,
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

  const handleChange = (e: React.ChangeEvent<HTMLInputElement | HTMLTextAreaElement>) => {
    const { name, value } = e.target
    setFormData((prev) => ({
      ...prev,
      [name]: name === "budget" ? Number.parseFloat(value) || 0 : value,
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
          <Link href="/dashboard/campaigns">
            <Button variant="ghost" size="sm" className="text-muted-foreground hover:bg-accent hover:text-foreground">
              <ArrowLeft className="h-4 w-4 mr-2" />
              Back to Campaigns
            </Button>
          </Link>
        </div>

        <div>
          <h1 className="text-3xl font-bold text-foreground">Create New Campaign</h1>
          <p className="text-muted-foreground mt-1">Design and launch your marketing campaign</p>
        </div>

        <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
          <div className="lg:col-span-2">
            <BlurredCard>
              <CardHeader>
                <CardTitle className="text-foreground">Campaign Details</CardTitle>
                <CardDescription className="text-muted-foreground">Configure your campaign settings and content</CardDescription>
              </CardHeader>
              <CardContent>
                <form className="space-y-6">
                  <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                    <div className="space-y-2">
                      <label htmlFor="name" className="text-sm font-medium text-foreground">
                        Campaign Name
                      </label>
                      <Input
                        id="name"
                        name="name"
                        value={formData.name}
                        onChange={handleChange}
                        placeholder="Enter campaign name"
                        required
                        className="bg-background/50 border-border focus:border-primary"
                      />
                    </div>

                    <div className="space-y-2">
                      <label htmlFor="campaign_type" className="text-sm font-medium text-foreground">
                        Campaign Type
                      </label>
                      <Select onValueChange={(value) => handleSelectChange("campaign_type", value)} value={formData.campaign_type} required>
                        <SelectTrigger className="w-full bg-background/50 border-border focus:border-primary">
                          <SelectValue placeholder="Select campaign type" />
                        </SelectTrigger>
                        <SelectContent>
                          <SelectItem value="discount">Discount</SelectItem>
                          <SelectItem value="points_bonus">Points Bonus</SelectItem>
                          <SelectItem value="free_item">Free Item</SelectItem>
                          <SelectItem value="cashback">Cashback</SelectItem>
                          <SelectItem value="referral">Referral</SelectItem>
                        </SelectContent>
                      </Select>
                    </div>
                  </div>

                  <div className="space-y-2">
                    <label htmlFor="description" className="text-sm font-medium text-foreground">
                      Description
                    </label>
                    <Textarea
                      id="description"
                      name="description"
                      value={formData.description}
                      onChange={handleChange}
                      placeholder="Describe your campaign objectives"
                      rows={3}
                      className="bg-background/50 border-border focus:border-primary"
                    />
                  </div>

                  <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                    <div className="space-y-2">
                      <label htmlFor="target_audience" className="text-sm font-medium text-foreground">
                        Target Audience
                      </label>
                      <Select onValueChange={(value) => handleSelectChange("target_audience", value)} value={formData.target_audience} required>
                        <SelectTrigger className="w-full bg-background/50 border-border focus:border-primary">
                          <SelectValue placeholder="Select target audience" />
                        </SelectTrigger>
                        <SelectContent>
                          <SelectItem value="all_customers">All Customers</SelectItem>
                          <SelectItem value="new_customers">New Customers</SelectItem>
                          <SelectItem value="regular_customers">Regular Customers</SelectItem>
                          <SelectItem value="vip_customers">VIP Customers</SelectItem>
                          <SelectItem value="at_risk_customers">At-Risk Customers</SelectItem>
                          <SelectItem value="churned_customers">Churned Customers</SelectItem>
                          <SelectItem value="custom_segment">Custom Segment</SelectItem>
                        </SelectContent>
                      </Select>
                    </div>

                    <div className="space-y-2">
                      <label htmlFor="budget" className="text-sm font-medium text-foreground">
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
                        className="bg-background/50 border-border focus:border-primary"
                      />
                    </div>
                  </div>

                  <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                    <div className="space-y-2">
                      <label htmlFor="start_date" className="text-sm font-medium text-foreground">
                        Start Date
                      </label>
                      <Input
                        id="start_date"
                        name="start_date"
                        type="datetime-local"
                        value={formData.start_date}
                        onChange={handleChange}
                        required
                        className="bg-background/50 border-border focus:border-primary"
                      />
                    </div>

                    <div className="space-y-2">
                      <label htmlFor="end_date" className="text-sm font-medium text-foreground">
                        End Date
                      </label>
                      <Input
                        id="end_date"
                        name="end_date"
                        type="datetime-local"
                        value={formData.end_date}
                        onChange={handleChange}
                        required
                        className="bg-background/50 border-border focus:border-primary"
                      />
                    </div>
                  </div>

                  <div className="space-y-2">
                    <label htmlFor="sms_message" className="text-sm font-medium text-foreground">
                      Campaign Message (SMS)
                    </label>
                    <Textarea
                      id="sms_message"
                      name="sms_message"
                      value={formData.sms_message}
                      onChange={handleChange}
                      placeholder="Enter your campaign message..."
                      rows={4}
                      className="bg-background/50 border-border focus:border-primary"
                    />
                    <p className="text-xs text-muted-foreground">{formData.sms_message.length}/160 characters (SMS limit)</p>
                  </div>

                  <div className="flex space-x-4">
                    <Button
                      type="button"
                      variant="outline"
                      onClick={(e) => handleSubmit(e, false)}
                      disabled={loading}
                      className="bg-background/50 border-border text-foreground hover:bg-accent"
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
            </BlurredCard>
          </div>

          <div className="space-y-6">
            <BlurredCard>
              <CardHeader>
                <CardTitle className="text-foreground">Campaign Preview</CardTitle>
                <CardDescription className="text-muted-foreground">How your campaign will appear</CardDescription>
              </CardHeader>
              <CardContent>
                <div className="space-y-4">
                  <div>
                    <p className="text-sm font-medium text-foreground">Campaign Name</p>
                    <p className="text-sm text-muted-foreground">{formData.name || "Untitled Campaign"}</p>
                  </div>

                  <div>
                    <p className="text-sm font-medium text-foreground">Type</p>
                    <Badge variant="outline" className="bg-secondary/50 text-secondary-foreground">{formData.campaign_type}</Badge>
                  </div>

                  <div>
                    <p className="text-sm font-medium text-foreground">Target</p>
                    <p className="text-sm text-muted-foreground">{formData.target_audience.replace("_", " ")}</p>
                  </div>

                  {formData.sms_message && (
                    <div>
                      <p className="text-sm font-medium text-foreground">Message Preview</p>
                      <div className="p-3 bg-background/50 rounded-lg border border-border/50">
                        <p className="text-sm text-muted-foreground">{formData.sms_message}</p>
                      </div>
                    </div>
                  )}
                </div>
              </CardContent>
            </BlurredCard>

            <BlurredCard>
              <CardHeader>
                <CardTitle className="text-foreground">Campaign Tips</CardTitle>
              </CardHeader>
              <CardContent>
                <div className="space-y-3 text-sm text-muted-foreground">
                  <div className="flex items-start space-x-2">
                    <div className="w-2 h-2 bg-primary rounded-full mt-1.5"></div>
                    <p>Keep SMS messages under 160 characters for best delivery rates</p>
                  </div>
                  <div className="flex items-start space-x-2">
                    <div className="w-2 h-2 bg-success rounded-full mt-1.5"></div>
                    <p>Personalize messages with customer names for higher engagement</p>
                  </div>
                  <div className="flex items-start space-x-2">
                    <div className="w-2 h-2 bg-brand-secondary rounded-full mt-1.5"></div>
                    <p>Schedule campaigns during peak customer activity hours</p>
                  </div>
                </div>
              </CardContent>
            </BlurredCard>
          </div>
        </div>
      </div>
    </DashboardLayout>
  )
}