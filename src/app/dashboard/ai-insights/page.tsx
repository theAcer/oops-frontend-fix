"use client"

import { useState } from "react"
import { DashboardLayout } from "@/components/layout/dashboard-layout"
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card"
import { Button } from "@/components/ui/button"
import { Badge } from "@/components/ui/badge"
import { Input } from "@/components/ui/input"
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from "@/components/ui/table"
import { useMerchantInsights, useChurnRisk, useCustomerInsights } from "@/hooks/use-api"
import { formatCurrency } from "@/lib/utils"
import { Brain, AlertTriangle, TrendingUp, Users, Target, Zap, Search } from "lucide-react"
import { apiService } from "@/services/api-service"
import { useAuth } from "@/contexts/auth-context"

export default function AIInsightsPage() {
  const [selectedCustomerId, setSelectedCustomerId] = useState("")
  const [trainingModels, setTrainingModels] = useState(false)
  const { user } = useAuth()

  const { data: merchantInsights, isLoading: insightsLoading, mutate: refreshInsights } = useMerchantInsights()
  const { data: churnRiskData, isLoading: churnLoading } = useChurnRisk()
  const { data: customerInsights, isLoading: customerInsightsLoading } = useCustomerInsights()

  const handleTrainModels = async () => {
    if (!user?.merchant_id) return

    setTrainingModels(true)
    try {
      await apiService.trainModels(user.merchant_id)
      refreshInsights()
    } catch (error) {
      console.error("Failed to train models:", error)
    } finally {
      setTrainingModels(false)
    }
  }

  return (
    <DashboardLayout>
      <div className="space-y-6">
        <div className="flex items-center justify-between">
          <div>
            <h1 className="text-3xl font-bold text-gray-900">AI Insights</h1>
            <p className="text-gray-600">AI-powered customer behavior analysis and business predictions</p>
          </div>
          <Button onClick={handleTrainModels} disabled={trainingModels}>
            <Brain className={`h-4 w-4 mr-2 ${trainingModels ? "animate-pulse" : ""}`} />
            {trainingModels ? "Training Models..." : "Train AI Models"}
          </Button>
        </div>

        {/* AI Overview Cards */}
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
          <Card>
            <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
              <CardTitle className="text-sm font-medium">Churn Risk Score</CardTitle>
              <AlertTriangle className="h-4 w-4 text-orange-500" />
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold text-orange-600">
                {merchantInsights?.average_churn_risk?.toFixed(1) || "0.0"}%
              </div>
              <p className="text-xs text-muted-foreground">Average across all customers</p>
            </CardContent>
          </Card>

          <Card>
            <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
              <CardTitle className="text-sm font-medium">Predicted CLV</CardTitle>
              <TrendingUp className="h-4 w-4 text-green-500" />
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold text-green-600">
                {merchantInsights ? formatCurrency(merchantInsights.average_lifetime_value || 0) : formatCurrency(0)}
              </div>
              <p className="text-xs text-muted-foreground">Average customer lifetime value</p>
            </CardContent>
          </Card>

          <Card>
            <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
              <CardTitle className="text-sm font-medium">High-Value Customers</CardTitle>
              <Users className="h-4 w-4 text-purple-500" />
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold text-purple-600">
                {merchantInsights?.high_value_customers_count || 0}
              </div>
              <p className="text-xs text-muted-foreground">Customers with high predicted value</p>
            </CardContent>
          </Card>

          <Card>
            <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
              <CardTitle className="text-sm font-medium">Campaign Readiness</CardTitle>
              <Target className="h-4 w-4 text-blue-500" />
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold text-blue-600">
                {merchantInsights?.campaign_readiness_score?.toFixed(0) || 0}%
              </div>
              <p className="text-xs text-muted-foreground">Optimal timing for campaigns</p>
            </CardContent>
          </Card>
        </div>

        {/* Churn Risk Analysis */}
        <Card>
          <CardHeader>
            <CardTitle className="flex items-center space-x-2">
              <AlertTriangle className="h-5 w-5 text-orange-500" />
              <span>Churn Risk Analysis</span>
            </CardTitle>
            <CardDescription>Customers at risk of churning - take action to retain them</CardDescription>
          </CardHeader>
          <CardContent>
            {churnLoading ? (
              <div className="flex items-center justify-center h-32">
                <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-primary"></div>
              </div>
            ) : churnRiskData?.high_risk_customers?.length > 0 ? (
              <Table>
                <TableHeader>
                  <TableRow>
                    <TableHead>Customer</TableHead>
                    <TableHead>Risk Score</TableHead>
                    <TableHead>Last Purchase</TableHead>
                    <TableHead>Total Spent</TableHead>
                    <TableHead>Recommended Action</TableHead>
                    <TableHead>Actions</TableHead>
                  </TableRow>
                </TableHeader>
                <TableBody>
                  {churnRiskData.high_risk_customers.slice(0, 5).map((customer: any) => (
                    <TableRow key={customer.customer_id}>
                      <TableCell className="font-medium">{customer.customer_name || customer.customer_id}</TableCell>
                      <TableCell>
                        <Badge
                          variant={
                            customer.churn_risk > 0.7
                              ? "destructive"
                              : customer.churn_risk > 0.4
                                ? "secondary"
                                : "outline"
                          }
                        >
                          {(customer.churn_risk * 100).toFixed(0)}%
                        </Badge>
                      </TableCell>
                      <TableCell>{customer.days_since_last_purchase} days ago</TableCell>
                      <TableCell>{formatCurrency(customer.total_spent)}</TableCell>
                      <TableCell className="text-sm">{customer.recommended_action}</TableCell>
                      <TableCell>
                        <Button variant="outline" size="sm" className="bg-transparent">
                          Send Offer
                        </Button>
                      </TableCell>
                    </TableRow>
                  ))}
                </TableBody>
              </Table>
            ) : (
              <p className="text-center text-gray-500 py-8">No high-risk customers identified</p>
            )}
          </CardContent>
        </Card>

        {/* Customer Insights */}
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center space-x-2">
                <Brain className="h-5 w-5 text-blue-500" />
                <span>Customer Behavior Insights</span>
              </CardTitle>
              <CardDescription>AI-powered analysis of customer patterns</CardDescription>
            </CardHeader>
            <CardContent>
              {customerInsightsLoading ? (
                <div className="flex items-center justify-center h-32">
                  <div className="animate-spin rounded-full h-6 w-6 border-b-2 border-primary"></div>
                </div>
              ) : (
                <div className="space-y-4">
                  <div className="p-4 bg-blue-50 rounded-lg">
                    <h4 className="font-medium text-blue-800 mb-2">Peak Shopping Hours</h4>
                    <p className="text-sm text-blue-600">
                      Most customers shop between 2-4 PM and 7-9 PM. Schedule campaigns accordingly.
                    </p>
                  </div>

                  <div className="p-4 bg-green-50 rounded-lg">
                    <h4 className="font-medium text-green-800 mb-2">Popular Product Categories</h4>
                    <p className="text-sm text-green-600">
                      Electronics and fashion items show highest engagement. Consider cross-selling opportunities.
                    </p>
                  </div>

                  <div className="p-4 bg-purple-50 rounded-lg">
                    <h4 className="font-medium text-purple-800 mb-2">Seasonal Trends</h4>
                    <p className="text-sm text-purple-600">
                      Revenue typically increases by 25% during holiday seasons. Plan inventory accordingly.
                    </p>
                  </div>

                  <div className="p-4 bg-orange-50 rounded-lg">
                    <h4 className="font-medium text-orange-800 mb-2">Customer Segments</h4>
                    <p className="text-sm text-orange-600">
                      3 distinct customer segments identified: Budget-conscious (45%), Premium (30%), Occasional (25%).
                    </p>
                  </div>
                </div>
              )}
            </CardContent>
          </Card>

          <Card>
            <CardHeader>
              <CardTitle className="flex items-center space-x-2">
                <Zap className="h-5 w-5 text-yellow-500" />
                <span>AI Recommendations</span>
              </CardTitle>
              <CardDescription>Actionable insights to grow your business</CardDescription>
            </CardHeader>
            <CardContent>
              <div className="space-y-4">
                <div className="flex items-start space-x-3 p-3 border rounded-lg">
                  <div className="w-2 h-2 bg-green-500 rounded-full mt-2"></div>
                  <div>
                    <p className="font-medium text-sm">Launch Retention Campaign</p>
                    <p className="text-xs text-gray-600">
                      Target 47 customers with personalized offers. Predicted 23% response rate.
                    </p>
                  </div>
                </div>

                <div className="flex items-start space-x-3 p-3 border rounded-lg">
                  <div className="w-2 h-2 bg-blue-500 rounded-full mt-2"></div>
                  <div>
                    <p className="font-medium text-sm">Optimize Loyalty Program</p>
                    <p className="text-xs text-gray-600">
                      Adjust point values for electronics category to increase engagement by 15%.
                    </p>
                  </div>
                </div>

                <div className="flex items-start space-x-3 p-3 border rounded-lg">
                  <div className="w-2 h-2 bg-purple-500 rounded-full mt-2"></div>
                  <div>
                    <p className="font-medium text-sm">Cross-sell Opportunity</p>
                    <p className="text-xs text-gray-600">
                      Customers buying phones show 67% likelihood to purchase accessories within 7 days.
                    </p>
                  </div>
                </div>

                <div className="flex items-start space-x-3 p-3 border rounded-lg">
                  <div className="w-2 h-2 bg-orange-500 rounded-full mt-2"></div>
                  <div>
                    <p className="font-medium text-sm">Inventory Planning</p>
                    <p className="text-xs text-gray-600">
                      Stock up on fashion items 2 weeks before payday cycles for 18% revenue boost.
                    </p>
                  </div>
                </div>
              </div>
            </CardContent>
          </Card>
        </div>

        {/* Individual Customer Analysis */}
        <Card>
          <CardHeader>
            <CardTitle>Individual Customer Analysis</CardTitle>
            <CardDescription>Get AI insights for specific customers</CardDescription>
          </CardHeader>
          <CardContent>
            <div className="flex space-x-4 mb-6">
              <div className="relative flex-1 max-w-sm">
                <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 text-gray-400 h-4 w-4" />
                <Input
                  placeholder="Enter customer ID..."
                  value={selectedCustomerId}
                  onChange={(e) => setSelectedCustomerId(e.target.value)}
                  className="pl-10"
                />
              </div>
              <Button disabled={!selectedCustomerId}>Analyze Customer</Button>
            </div>

            {selectedCustomerId && (
              <div className="p-4 bg-gray-50 rounded-lg">
                <p className="text-sm text-gray-600">
                  Enter a customer ID above to get detailed AI analysis including churn risk, lifetime value prediction,
                  next purchase timing, and personalized offer recommendations.
                </p>
              </div>
            )}
          </CardContent>
        </Card>
      </div>
    </DashboardLayout>
  )
}
