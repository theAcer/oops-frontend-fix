"use client"

import { useState } from "react"
import { DashboardLayout } from "@/components/layout/dashboard-layout"
import { CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card"
import { Button } from "@/components/ui/button"
import { Badge } from "@/components/ui/badge"
import { Input } from "@/components/ui/input"
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from "@/components/ui/table"
import { useMerchantInsights, useChurnRisk, useCustomerInsights } from "@/hooks/use-api"
import { formatCurrency } from "@/lib/utils"
import { Brain, AlertTriangle, TrendingUp, Users, Target, Zap, Search } from "lucide-react"
import { apiService } from "@/services/api-service"
import { useAuth } from "@/contexts/auth-context"
import { BlurredCard } from "@/components/blurred-card"

export default function AIInsightsPage() {
  const [selectedCustomerId, setSelectedCustomerId] = useState("")
  const [trainingModels, setTrainingModels] = useState(false)
  const { user } = useAuth()

  const { data: merchantInsights, mutate: refreshInsights } = useMerchantInsights()
  const { data: churnRiskData, isLoading: churnLoading } = useChurnRisk()
  const { isLoading: customerInsightsLoading } = useCustomerInsights()

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
      <div className="space-y-8">
        <div className="flex items-center justify-between">
          <div>
            <h1 className="text-3xl font-bold text-foreground">AI Insights</h1>
            <p className="text-muted-foreground mt-1">AI-powered customer behavior analysis and business predictions</p>
          </div>
          <Button onClick={handleTrainModels} disabled={trainingModels}>
            <Brain className={`h-4 w-4 mr-2 ${trainingModels ? "animate-pulse" : ""}`} />
            {trainingModels ? "Training Models..." : "Train AI Models"}
          </Button>
        </div>

        {/* AI Overview Cards */}
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
          <BlurredCard>
            <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
              <CardTitle className="text-sm font-medium text-muted-foreground">Churn Risk Score</CardTitle>
              <AlertTriangle className="h-4 w-4 text-warning" />
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold text-warning">
                {merchantInsights?.average_churn_risk?.toFixed(1) || "0.0"}%
              </div>
              <p className="text-xs text-muted-foreground">Average across all customers</p>
            </CardContent>
          </BlurredCard>

          <BlurredCard>
            <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
              <CardTitle className="text-sm font-medium text-muted-foreground">Predicted CLV</CardTitle>
              <TrendingUp className="h-4 w-4 text-success" />
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold text-success">
                {merchantInsights ? formatCurrency(merchantInsights.average_lifetime_value || 0) : formatCurrency(0)}
              </div>
              <p className="text-xs text-muted-foreground">Average customer lifetime value</p>
            </CardContent>
          </BlurredCard>

          <BlurredCard>
            <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
              <CardTitle className="text-sm font-medium text-muted-foreground">High-Value Customers</CardTitle>
              <Users className="h-4 w-4 text-brand-secondary" />
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold text-brand-secondary">
                {merchantInsights?.high_value_customers_count || 0}
              </div>
              <p className="text-xs text-muted-foreground">Customers with high predicted value</p>
            </CardContent>
          </BlurredCard>

          <BlurredCard>
            <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
              <CardTitle className="text-sm font-medium text-muted-foreground">Campaign Readiness</CardTitle>
              <Target className="h-4 w-4 text-primary" />
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold text-primary">
                {merchantInsights?.campaign_readiness_score?.toFixed(0) || 0}%
              </div>
              <p className="text-xs text-muted-foreground">Optimal timing for campaigns</p>
            </CardContent>
          </BlurredCard>
        </div>

        {/* Churn Risk Analysis */}
        <BlurredCard>
          <CardHeader>
            <CardTitle className="flex items-center space-x-2 text-foreground">
              <AlertTriangle className="h-5 w-5 text-warning" />
              <span>Churn Risk Analysis</span>
            </CardTitle>
            <CardDescription className="text-muted-foreground">Customers at risk of churning - take action to retain them</CardDescription>
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
                      <TableCell className="font-medium text-foreground">{customer.customer_name || customer.customer_id}</TableCell>
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
                      <TableCell className="text-muted-foreground">{customer.days_since_last_purchase} days ago</TableCell>
                      <TableCell className="text-foreground">{formatCurrency(customer.total_spent)}</TableCell>
                      <TableCell className="text-sm text-muted-foreground">{customer.recommended_action}</TableCell>
                      <TableCell>
                        <Button variant="outline" size="sm" className="bg-background/50 border-border text-foreground hover:bg-accent">
                          Send Offer
                        </Button>
                      </TableCell>
                    </TableRow>
                  ))}
                </TableBody>
              </Table>
            ) : (
              <p className="text-center text-muted-foreground py-8">No high-risk customers identified</p>
            )}
          </CardContent>
        </BlurredCard>

        {/* Customer Insights */}
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
          <BlurredCard>
            <CardHeader>
              <CardTitle className="flex items-center space-x-2 text-foreground">
                <Brain className="h-5 w-5 text-primary" />
                <span>Customer Behavior Insights</span>
              </CardTitle>
              <CardDescription className="text-muted-foreground">AI-powered analysis of customer patterns</CardDescription>
            </CardHeader>
            <CardContent>
              {customerInsightsLoading ? (
                <div className="flex items-center justify-center h-32">
                  <div className="animate-spin rounded-full h-6 w-6 border-b-2 border-primary"></div>
                </div>
              ) : (
                <div className="space-y-4">
                  <div className="p-4 bg-primary/10 rounded-lg border border-primary/20">
                    <h4 className="font-medium text-primary mb-2">Peak Shopping Hours</h4>
                    <p className="text-sm text-muted-foreground">
                      Most customers shop between 2-4 PM and 7-9 PM. Schedule campaigns accordingly.
                    </p>
                  </div>

                  <div className="p-4 bg-success/10 rounded-lg border border-success/20">
                    <h4 className="font-medium text-success mb-2">Popular Product Categories</h4>
                    <p className="text-sm text-muted-foreground">
                      Electronics and fashion items show highest engagement. Consider cross-selling opportunities.
                    </p>
                  </div>

                  <div className="p-4 bg-brand-secondary/10 rounded-lg border border-brand-secondary/20">
                    <h4 className="font-medium text-brand-secondary mb-2">Seasonal Trends</h4>
                    <p className="text-sm text-muted-foreground">
                      Revenue typically increases by 25% during holiday seasons. Plan inventory accordingly.
                    </p>
                  </div>

                  <div className="p-4 bg-warning/10 rounded-lg border border-warning/20">
                    <h4 className="font-medium text-warning mb-2">Customer Segments</h4>
                    <p className="text-sm text-muted-foreground">
                      3 distinct customer segments identified: Budget-conscious (45%), Premium (30%), Occasional (25%).
                    </p>
                  </div>
                </div>
              )}
            </CardContent>
          </BlurredCard>

          <BlurredCard>
            <CardHeader>
              <CardTitle className="flex items-center space-x-2 text-foreground">
                <Zap className="h-5 w-5 text-brand-secondary" />
                <span>AI Recommendations</span>
              </CardTitle>
              <CardDescription className="text-muted-foreground">Actionable insights to grow your business</CardDescription>
            </CardHeader>
            <CardContent>
              <div className="space-y-4">
                <div className="flex items-start space-x-3 p-3 border border-border/50 rounded-lg bg-background/50">
                  <div className="w-2 h-2 bg-success rounded-full mt-2"></div>
                  <div>
                    <p className="font-medium text-sm text-foreground">Launch Retention Campaign</p>
                    <p className="text-xs text-muted-foreground">
                      Target 47 customers with personalized offers. Predicted 23% response rate.
                    </p>
                  </div>
                </div>

                <div className="flex items-start space-x-3 p-3 border border-border/50 rounded-lg bg-background/50">
                  <div className="w-2 h-2 bg-primary rounded-full mt-2"></div>
                  <div>
                    <p className="font-medium text-sm text-foreground">Optimize Loyalty Program</p>
                    <p className="text-xs text-muted-foreground">
                      Adjust point values for electronics category to increase engagement by 15%.
                    </p>
                  </div>
                </div>

                <div className="flex items-start space-x-3 p-3 border border-border/50 rounded-lg bg-background/50">
                  <div className="w-2 h-2 bg-brand-secondary rounded-full mt-2"></div>
                  <div>
                    <p className="font-medium text-sm text-foreground">Cross-sell Opportunity</p>
                    <p className="text-xs text-muted-foreground">
                      Customers buying phones show 67% likelihood to purchase accessories within 7 days.
                    </p>
                  </div>
                </div>

                <div className="flex items-start space-x-3 p-3 border border-border/50 rounded-lg bg-background/50">
                  <div className="w-2 h-2 bg-warning rounded-full mt-2"></div>
                  <div>
                    <p className="font-medium text-sm text-foreground">Inventory Planning</p>
                    <p className="text-xs text-muted-foreground">
                      Stock up on fashion items 2 weeks before payday cycles for 18% revenue boost.
                    </p>
                  </div>
                </div>
              </div>
            </CardContent>
          </BlurredCard>
        </div>

        {/* Individual Customer Analysis */}
        <BlurredCard>
          <CardHeader>
            <CardTitle className="text-foreground">Individual Customer Analysis</CardTitle>
            <CardDescription className="text-muted-foreground">Get AI insights for specific customers</CardDescription>
          </CardHeader>
          <CardContent>
            <div className="flex flex-col sm:flex-row space-y-4 sm:space-y-0 sm:space-x-4 mb-6">
              <div className="relative flex-1 max-w-sm">
                <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 text-muted-foreground h-4 w-4" />
                <Input
                  placeholder="Enter customer ID..."
                  value={selectedCustomerId}
                  onChange={(e) => setSelectedCustomerId(e.target.value)}
                  className="pl-10 bg-background/50 border-border focus:border-primary"
                />
              </div>
              <Button disabled={!selectedCustomerId}>Analyze Customer</Button>
            </div>

            {selectedCustomerId && (
              <div className="p-4 bg-background/50 rounded-lg border border-border/50">
                <p className="text-sm text-muted-foreground">
                  Enter a customer ID above to get detailed AI analysis including churn risk, lifetime value prediction,
                  next purchase timing, and personalized offer recommendations.
                </p>
              </div>
            )}
          </CardContent>
        </BlurredCard>
      </div>
    </DashboardLayout>
  )
}