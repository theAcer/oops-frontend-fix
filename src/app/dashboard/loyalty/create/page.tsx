"use client"

import type React from "react"

import { useState } from "react"
import { useRouter } from "next/navigation"
import { DashboardLayout } from "@/components/layout/dashboard-layout"
import { CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card"
import { Button } from "@/components/ui/button"
import { Input } from "@/components/ui/input"
import { Badge } from "@/components/ui/badge"
import { Textarea } from "@/components/ui/textarea" // Import Textarea
import { apiService } from "@/services/api-service"
import { useAuth } from "@/contexts/auth-context"
import { ArrowLeft, Save, Play } from "lucide-react"
import Link from "next/link"
import { AnimatedButton } from "@/components/animated-button"
import { BlurredCard } from "@/components/blurred-card"

export default function CreateLoyaltyProgramPage() {
  const router = useRouter()
  const { user } = useAuth()
  const [loading, setLoading] = useState(false)
  const [formData, setFormData] = useState({
    name: "",
    description: "",
    program_type: "points", // Default to points
    points_per_currency: 1,
    minimum_spend: 100,
  })

  const handleSubmit = async (e: React.FormEvent, activate = false) => {
    e.preventDefault()
    if (!user?.merchant_id) return

    setLoading(true)
    try {
      const programData = {
        ...formData,
        merchant_id: user.merchant_id,
        is_active: activate,
      }

      const program = await apiService.createLoyaltyProgram(programData)

      if (activate) {
        await apiService.activateLoyaltyProgram(program.id)
      }

      router.push("/dashboard/loyalty")
    } catch (error) {
      console.error("Failed to create loyalty program:", error)
    } finally {
      setLoading(false)
    }
  }

  const handleChange = (e: React.ChangeEvent<HTMLInputElement | HTMLTextAreaElement | HTMLSelectElement>) => {
    const { name, value } = e.target
    setFormData((prev) => ({
      ...prev,
      [name]: name === "points_per_currency" || name === "minimum_spend" ? Number.parseFloat(value) || 0 : value,
    }))
  }

  return (
    <DashboardLayout>
      <div className="space-y-8">
        <div className="flex items-center space-x-4">
          <Link href="/dashboard/loyalty">
            <Button variant="ghost" size="sm" className="text-muted-foreground hover:bg-accent hover:text-foreground">
              <ArrowLeft className="h-4 w-4 mr-2" />
              Back to Loyalty Programs
            </Button>
          </Link>
        </div>

        <div>
          <h1 className="text-3xl font-bold text-foreground">Create Loyalty Program</h1>
          <p className="text-muted-foreground mt-1">Design a reward program to increase customer retention</p>
        </div>

        <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
          <div className="lg:col-span-2">
            <BlurredCard>
              <CardHeader>
                <CardTitle className="text-foreground">Program Configuration</CardTitle>
                <CardDescription className="text-muted-foreground">Set up your loyalty program rules and rewards</CardDescription>
              </CardHeader>
              <CardContent>
                <form className="space-y-6">
                  <div className="space-y-2">
                    <label htmlFor="name" className="text-sm font-medium text-foreground">
                      Program Name
                    </label>
                    <Input
                      id="name"
                      name="name"
                      value={formData.name}
                      onChange={handleChange}
                      placeholder="e.g., VIP Rewards Program"
                      required
                      className="bg-background/50 border-border focus:border-primary"
                    />
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
                      placeholder="Describe the benefits and how customers can earn rewards"
                      rows={3}
                      className="bg-background/50 border-border focus:border-primary"
                    />
                  </div>

                  <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                    <div className="space-y-2">
                      <label htmlFor="points_per_currency" className="text-sm font-medium text-foreground">
                        Points per KES Spent
                      </label>
                      <Input
                        id="points_per_currency"
                        name="points_per_currency"
                        type="number"
                        value={formData.points_per_currency}
                        onChange={handleChange}
                        placeholder="1"
                        min="0.1"
                        step="0.1"
                        required
                        className="bg-background/50 border-border focus:border-primary"
                      />
                      <p className="text-xs text-muted-foreground">How many points customers earn per KES spent</p>
                    </div>

                    <div className="space-y-2">
                      <label htmlFor="minimum_spend" className="text-sm font-medium text-foreground">
                        Minimum Spend (KES)
                      </label>
                      <Input
                        id="minimum_spend"
                        name="minimum_spend"
                        type="number"
                        value={formData.minimum_spend}
                        onChange={handleChange}
                        placeholder="100"
                        min="0"
                        step="10"
                        required
                        className="bg-background/50 border-border focus:border-primary"
                      />
                      <p className="text-xs text-muted-foreground">Minimum purchase amount to earn points</p>
                    </div>
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
                      <Play className="h-4 w-4 mr-2" />
                      {loading ? "Creating..." : "Create & Activate"}
                    </AnimatedButton>
                  </div>
                </form>
              </CardContent>
            </BlurredCard>
          </div>

          <div className="space-y-6">
            <BlurredCard>
              <CardHeader>
                <CardTitle className="text-foreground">Program Preview</CardTitle>
                <CardDescription className="text-muted-foreground">How your program will work</CardDescription>
              </CardHeader>
              <CardContent>
                <div className="space-y-4">
                  <div>
                    <p className="text-sm font-medium text-foreground">Program Name</p>
                    <p className="text-sm text-muted-foreground">{formData.name || "Untitled Program"}</p>
                  </div>

                  <div>
                    <p className="text-sm font-medium text-foreground">Earning Rate</p>
                    <Badge variant="outline" className="bg-secondary/50 text-secondary-foreground">
                      {formData.points_per_currency} point{formData.points_per_currency !== 1 ? "s" : ""} per KES
                    </Badge>
                  </div>

                  <div>
                    <p className="text-sm font-medium text-foreground">Example Calculation</p>
                    <div className="p-3 bg-background/50 rounded-lg border border-border/50">
                      <p className="text-sm text-muted-foreground">
                        Customer spends KES 500
                        <br />
                        Earns: {500 * formData.points_per_currency} points
                      </p>
                    </div>
                  </div>

                  <div>
                    <p className="text-sm font-medium text-foreground">Minimum Purchase</p>
                    <p className="text-sm text-muted-foreground">KES {formData.minimum_spend}</p>
                  </div>
                </div>
              </CardContent>
            </BlurredCard>

            <BlurredCard>
              <CardHeader>
                <CardTitle className="text-foreground">Program Benefits</CardTitle>
              </CardHeader>
              <CardContent>
                <div className="space-y-3 text-sm text-muted-foreground">
                  <div className="flex items-start space-x-2">
                    <div className="w-2 h-2 bg-success rounded-full mt-1.5"></div>
                    <p>Increase customer retention by up to 30%</p>
                  </div>
                  <div className="flex items-start space-x-2">
                    <div className="w-2 h-2 bg-primary rounded-full mt-1.5"></div>
                    <p>Encourage repeat purchases and higher spending</p>
                  </div>
                  <div className="flex items-start space-x-2">
                    <div className="w-2 h-2 bg-brand-secondary rounded-full mt-1.5"></div>
                    <p>Build stronger customer relationships</p>
                  </div>
                  <div className="flex items-start space-x-2">
                    <div className="w-2 h-2 bg-warning rounded-full mt-1.5"></div>
                    <p>Gain valuable customer behavior insights</p>
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