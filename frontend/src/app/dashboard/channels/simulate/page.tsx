"use client"

import type React from "react"
import { useState } from "react"
import { DashboardLayout } from "@/components/layout/dashboard-layout"
import { CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card"
import { Button } from "@/components/ui/button"
import { Input } from "@/components/ui/input"
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select"
import { Badge } from "@/components/ui/badge"
import { ArrowLeft, Play, TestTube, CheckCircle, XCircle, Clock } from "lucide-react"
import Link from "next/link"
import { toast } from "react-hot-toast"
import { BlurredCard } from "@/components/blurred-card"

interface SimulationResult {
  success: boolean
  transaction_id?: string
  message: string
  details?: any
}

export default function SimulatePaymentPage() {
  const [isOpen, setIsOpen] = useState(false)
  const [formData, setFormData] = useState({
    channelId: "",
    amount: "",
    customerPhone: "",
    billRefNumber: "",
  })
  const [result, setResult] = useState<SimulationResult | null>(null)
  const [loading, setLoading] = useState(false)

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    setLoading(true)
    setResult(null)

    try {
      // TODO: Replace with actual API call
      // const response = await apiService.simulateMpesaTransaction(
      //   parseInt(formData.channelId),
      //   {
      //     amount: parseFloat(formData.amount),
      //     customer_phone: formData.customerPhone,
      //     bill_ref: formData.billRefNumber
      //   }
      // )

      // Simulate API delay
      await new Promise(resolve => setTimeout(resolve, 2000))

      // Mock successful response
      const mockResult: SimulationResult = {
        success: true,
        transaction_id: "TEST" + Date.now(),
        message: "Payment simulation completed successfully",
        details: {
          amount: formData.amount,
          phone: formData.customerPhone,
          reference: formData.billRefNumber,
          status: "Completed"
        }
      }

      setResult(mockResult)
      toast.success("Payment simulation completed")

    } catch (error: any) {
      const errorResult: SimulationResult = {
        success: false,
        message: error.message || "Simulation failed",
        details: error.response?.data || null
      }
      setResult(errorResult)
      toast.error("Payment simulation failed")
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

  const resetForm = () => {
    setFormData({
      channelId: "",
      amount: "",
      customerPhone: "",
      billRefNumber: "",
    })
    setResult(null)
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
            <h1 className="text-3xl font-bold text-foreground">Sandbox Simulation</h1>
            <p className="text-muted-foreground mt-1">Test your M-Pesa integration with simulated transactions</p>
          </div>
        </div>

        <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
          {/* Simulation Form */}
          <BlurredCard>
            <CardHeader>
              <CardTitle className="text-foreground flex items-center">
                <TestTube className="h-5 w-5 mr-2" />
                Simulate Payment
              </CardTitle>
              <CardDescription className="text-muted-foreground">
                Test your M-Pesa channel with a simulated transaction
              </CardDescription>
            </CardHeader>
            <CardContent>
              <form onSubmit={handleSubmit} className="space-y-6">
                <div className="space-y-2">
                  <label htmlFor="channelId" className="text-sm font-medium text-foreground">
                    Channel
                  </label>
                  <Select onValueChange={(value) => handleSelectChange("channelId", value)} value={formData.channelId} required>
                    <SelectTrigger className="w-full bg-background/50 border-border focus:border-primary">
                      <SelectValue placeholder="Select a channel" />
                    </SelectTrigger>
                    <SelectContent>
                      <SelectItem value="1">Main PayBill (Sandbox)</SelectItem>
                      <SelectItem value="2">Test Channel (Sandbox)</SelectItem>
                    </SelectContent>
                  </Select>
                </div>

                <div className="space-y-2">
                  <label htmlFor="amount" className="text-sm font-medium text-foreground">
                    Amount (KES)
                  </label>
                  <Input
                    id="amount"
                    name="amount"
                    type="number"
                    step="0.01"
                    min="1"
                    value={formData.amount}
                    onChange={handleChange}
                    required
                    placeholder="100.00"
                    className="bg-background/50 border-border focus:border-primary"
                  />
                </div>

                <div className="space-y-2">
                  <label htmlFor="customerPhone" className="text-sm font-medium text-foreground">
                    Customer Phone
                  </label>
                  <Input
                    id="customerPhone"
                    name="customerPhone"
                    type="tel"
                    value={formData.customerPhone}
                    onChange={handleChange}
                    required
                    placeholder="254712345678"
                    className="bg-background/50 border-border focus:border-primary"
                  />
                </div>

                <div className="space-y-2">
                  <label htmlFor="billRefNumber" className="text-sm font-medium text-foreground">
                    Bill Reference (Optional)
                  </label>
                  <Input
                    id="billRefNumber"
                    name="billRefNumber"
                    type="text"
                    value={formData.billRefNumber}
                    onChange={handleChange}
                    placeholder="Invoice #12345"
                    className="bg-background/50 border-border focus:border-primary"
                  />
                </div>

                <div className="bg-blue-50 dark:bg-blue-950/20 p-4 rounded-lg">
                  <div className="flex items-start space-x-3">
                    <TestTube className="h-5 w-5 text-blue-500 mt-0.5" />
                    <div>
                      <h4 className="font-medium text-blue-900 dark:text-blue-100">Sandbox Mode</h4>
                      <p className="text-sm text-blue-700 dark:text-blue-300 mt-1">
                        This simulation only works with channels in sandbox environment.
                        No real money will be transferred.
                      </p>
                    </div>
                  </div>
                </div>

                <div className="flex space-x-4">
                  <Button type="submit" className="flex-1" disabled={loading}>
                    <Play className="h-4 w-4 mr-2" />
                    {loading ? "Simulating..." : "Run Simulation"}
                  </Button>
                  <Button type="button" variant="outline" onClick={resetForm}>
                    Reset
                  </Button>
                </div>
              </form>
            </CardContent>
          </BlurredCard>

          {/* Results Panel */}
          <BlurredCard>
            <CardHeader>
              <CardTitle className="text-foreground">Simulation Results</CardTitle>
              <CardDescription className="text-muted-foreground">
                View the results of your payment simulation
              </CardDescription>
            </CardHeader>
            <CardContent>
              {result ? (
                <div className="space-y-4">
                  <div className="flex items-center space-x-2">
                    {result.success ? (
                      <Badge variant="default" className="bg-green-100 text-green-800 border-green-200">
                        <CheckCircle className="w-3 h-3 mr-1" />
                        Success
                      </Badge>
                    ) : (
                      <Badge variant="destructive">
                        <XCircle className="w-3 h-3 mr-1" />
                        Failed
                      </Badge>
                    )}
                  </div>

                  <div className="space-y-2">
                    <p className="text-sm font-medium text-foreground">Transaction ID</p>
                    <p className="text-sm text-muted-foreground font-mono">
                      {result.transaction_id || "N/A"}
                    </p>
                  </div>

                  <div className="space-y-2">
                    <p className="text-sm font-medium text-foreground">Message</p>
                    <p className="text-sm text-muted-foreground">{result.message}</p>
                  </div>

                  {result.details && (
                    <div className="space-y-2">
                      <p className="text-sm font-medium text-foreground">Details</p>
                      <div className="bg-muted/50 p-3 rounded text-xs font-mono">
                        {JSON.stringify(result.details, null, 2)}
                      </div>
                    </div>
                  )}

                  <Button onClick={resetForm} variant="outline" className="w-full">
                    Run Another Simulation
                  </Button>
                </div>
              ) : (
                <div className="text-center py-8 text-muted-foreground">
                  <TestTube className="h-12 w-12 mx-auto mb-4 opacity-50" />
                  <p>Run a simulation to see results here</p>
                </div>
              )}
            </CardContent>
          </BlurredCard>
        </div>

        {/* Transaction History */}
        <BlurredCard>
          <CardHeader>
            <CardTitle className="text-foreground">Recent Simulations</CardTitle>
            <CardDescription className="text-muted-foreground">
              History of your recent payment simulations
            </CardDescription>
          </CardHeader>
          <CardContent>
            <div className="text-center py-8 text-muted-foreground">
              <Clock className="h-12 w-12 mx-auto mb-4 opacity-50" />
              <p>No recent simulations</p>
              <p className="text-sm">Your simulation history will appear here</p>
            </div>
          </CardContent>
        </BlurredCard>
      </div>
    </DashboardLayout>
  )
}
