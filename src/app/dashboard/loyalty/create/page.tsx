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
import { ArrowLeft, Save, Play } from "lucide-react"
import Link from "next/link"
import { AnimatedButton } from "@/components/animated-button" // Import AnimatedButton

export default function CreateLoyaltyProgramPage() {
  const router = useRouter()
  const { user } = useAuth()
  const [loading, setLoading] = useState(false)
  const [formData, setFormData] = useState({
    name: "",
    description: "",
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

  const handleChange = (e: React.ChangeEvent<HTMLInputElement | HTMLTextAreaElement>) => {
    const { name, value } = e.target
    setFormData((prev) => ({
      ...prev,
      [name]: name === "points_per_currency" || name === "minimum_spend" ? Number.parseFloat(value) || 0 : value,
    }))
  }

  return (
    <DashboardLayout>
      <div className="space-y-6">
        <div className="flex items-center space-x-4">
          <Link href="/dashboard/loyalty">
            <Button variant="ghost" size="sm">
              <ArrowLeft className="h-4 w-4 mr-2" />
              Back to Loyalty Programs
            </Button>
          </Link>
        </div>

        <div>
          <h1 className="text-3xl font-bold text-gray-900">Create Loyalty Program</h1>
          <p className="text-gray-600">Design a reward program to increase customer retention</p>
        </div>

        <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
          <div className="lg:col-span-2">
            <Card>
              <CardHeader>
                <CardTitle>Program Configuration</CardTitle>
                <CardDescription>Set up your loyalty program rules and rewards</CardDescription>
              </CardHeader>
              <CardContent>
                <form className="space-y-6">
                  <div className="space-y-2">
                    <label htmlFor="name" className="text-sm font-medium">
                      Program Name
                    </label>
                    <Input
                      id="name"
                      name="name"
                      value={formData.name}
                      onChange={handleChange}
                      placeholder="e.g., VIP Rewards Program"
                      required
                    />
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
                      placeholder="Describe the benefits and how customers can earn rewards"
                      rows={3}
                      className="flex w-full rounded-md border border-input bg-background px-3 py-2 text-sm ring-offset-background focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring focus-visible:ring-offset-2"
                    />
                  </div>

                  <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                    <div className="space-y-2">
                      <label htmlFor="points_per_currency" className="text-sm font-medium">
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
                      />
                      <p className="text-xs text-gray-500">How many points customers earn per KES spent</p>
                    </div>

                    <div className="space-y-2">
                      <label htmlFor="minimum_spend" className="text-sm font-medium">
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
                      />
                      <p className="text-xs text-gray-500">Minimum purchase amount to earn points</p>
                    </div>
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
                      <Play className="h-4 w-4 mr-2" />
                      {loading ? "Creating..." : "Create & Activate"}
                    </AnimatedButton>
                  </div>
                </form>
              </CardContent>
            </Card>
          </div>

          <div className="space-y-6">
            <Card>
              <CardHeader>
                <CardTitle>Program Preview</CardTitle>
                <CardDescription>How your program will work</CardDescription>
              </CardHeader>
              <CardContent>
                <div className="space-y-4">
                  <div>
                    <p className="text-sm font-medium">Program Name</p>
                    <p className="text-sm text-gray-600">{formData.name || "Untitled Program"}</p>
                  </div>

                  <div>
                    <p className="text-sm font-medium">Earning Rate</p>
                    <Badge variant="outline">
                      {formData.points_per_currency} point{formData.points_per_currency !== 1 ? "s" : ""} per KES
                    </Badge>
                  </div>

                  <div>
                    <p className="text-sm font-medium">Example Calculation</p>
                    <div className="p-3 bg-gray-50 rounded-lg">
                      <p className="text-sm">
                        Customer spends KES 500
                        <br />
                        Earns: {500 * formData.points_per_currency} points
                      </p>
                    </div>
                  </div>

                  <div>
                    <p className="text-sm font-medium">Minimum Purchase</p>
                    <p className="text-sm text-gray-600">KES {formData.minimum_spend}</p>
                  </div>
                </div>
              </CardContent>
            </Card>

            <Card>
              <CardHeader>
                <CardTitle>Program Benefits</CardTitle>
              </CardHeader>
              <CardContent>
                <div className="space-y-3 text-sm">
                  <div className="flex items-start space-x-2">
                    <div className="w-2 h-2 bg-green-500 rounded-full mt-1.5"></div>
                    <p>Increase customer retention by up to 30%</p>
                  </div>
                  <div className="flex items-start space-x-2">
                    <div className="w-2 h-2 bg-blue-500 rounded-full mt-1.5"></div>
                    <p>Encourage repeat purchases and higher spending</p>
                  </div>
                  <div className="flex items-start space-x-2">
                    <div className="w-2 h-2 bg-purple-500 rounded-full mt-1.5"></div>
                    <p>Build stronger customer relationships</p>
                  </div>
                  <div className="flex items-start space-x-2">
                    <div className="w-2 h-2 bg-orange-500 rounded-full mt-1.5"></div>
                    <p>Gain valuable customer behavior insights</p>
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