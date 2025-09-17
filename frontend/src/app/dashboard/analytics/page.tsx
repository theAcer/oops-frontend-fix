"use client"

import { DashboardLayout } from "@/components/layout/dashboard-layout"
import { CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card"
import { Button } from "@/components/ui/button"
import { Badge } from "@/components/ui/badge"
import { RevenueChart } from "@/components/charts/revenue-chart"
import { CustomerChart } from "@/components/charts/customer-chart"
import { LoyaltyChart } from "@/components/charts/loyalty-chart"
import {
  useDashboardAnalytics,
  useRevenueAnalytics,
  useCustomerAnalytics,
  useLoyaltyAnalytics,
  useRealTimeMetrics,
} from "@/hooks/use-api"
import { formatCurrency } from "@/lib/utils"
import { TrendingUp, Users, CreditCard, Target, Clock } from "lucide-react"
import { BlurredCard } from "@/components/blurred-card"

export default function AnalyticsPage() {
  const { data: dashboardData } = useDashboardAnalytics()
  const { data: revenueData, isLoading: revenueLoading } = useRevenueAnalytics()
  const { data: customerData, isLoading: customerLoading } = useCustomerAnalytics()
  const { data: loyaltyData, isLoading: loyaltyLoading } = useLoyaltyAnalytics()
  const { data: realTimeData, isLoading: realTimeLoading } = useRealTimeMetrics()

  // Mock data for charts (replace with real data from API)
  // These are used in the JSX, so no changes needed for unused vars.

  return (
    <DashboardLayout>
      <div className="space-y-8">
        <div className="flex items-center justify-between">
          <div>
            <h1 className="text-3xl font-bold text-foreground">Analytics</h1>
            <p className="text-muted-foreground mt-1">Comprehensive business insights and performance metrics</p>
          </div>
          <Button variant="outline" className="bg-background/50 border-border text-foreground hover:bg-accent">
            <Clock className="h-4 w-4 mr-2" />
            Real-time View
          </Button>
        </div>

        {/* Real-time Metrics */}
        <BlurredCard>
          <CardHeader>
            <CardTitle className="flex items-center space-x-2 text-foreground">
              <Clock className="h-5 w-5 text-primary" />
              <span>Today&apos;s Performance</span>
            </CardTitle>
            <CardDescription className="text-muted-foreground">Live metrics updated every 10 seconds</CardDescription>
          </CardHeader>
          <CardContent>
            {realTimeLoading ? (
              <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
                {[...Array(4)].map((_, i) => (
                  <div key={i} className="animate-pulse">
                    <div className="h-4 bg-muted rounded w-1/2 mb-2"></div>
                    <div className="h-8 bg-muted rounded w-3/4"></div>
                  </div>
                ))}
              </div>
            ) : (
              <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
                <div className="text-center">
                  <p className="text-sm text-muted-foreground">Today&apos;s Revenue</p>
                  <p className="text-2xl font-bold text-success">
                    {realTimeData ? formatCurrency(realTimeData.today_revenue || 0) : formatCurrency(0)}
                  </p>
                </div>
                <div className="text-center">
                  <p className="text-sm text-muted-foreground">Today&apos;s Transactions</p>
                  <p className="text-2xl font-bold text-primary">{realTimeData?.today_transactions || 0}</p>
                </div>
                <div className="text-center">
                  <p className="text-sm text-muted-foreground">New Customers</p>
                  <p className="text-2xl font-bold text-brand-secondary">{realTimeData?.today_customers || 0}</p>
                </div>
                <div className="text-center">
                  <p className="text-sm text-muted-foreground">Avg. Transaction Today</p>
                  <p className="text-2xl font-bold text-warning">{realTimeData ? formatCurrency(realTimeData.avg_transaction_today || 0) : formatCurrency(0)}</p>
                </div>
              </div>
            )}
          </CardContent>
        </BlurredCard>

        {/* Key Metrics */}
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
          <BlurredCard>
            <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
              <CardTitle className="text-sm font-medium text-muted-foreground">Revenue Growth</CardTitle>
              <TrendingUp className="h-4 w-4 text-muted-foreground" />
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold text-success">
                +{dashboardData?.growth_metrics?.revenue_growth?.toFixed(1) || 0}%
              </div>
              <p className="text-xs text-muted-foreground">vs last period</p>
            </CardContent>
          </BlurredCard>

          <BlurredCard>
            <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
              <CardTitle className="text-sm font-medium text-muted-foreground">Unique Customers</CardTitle>
              <Users className="h-4 w-4 text-muted-foreground" />
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold text-primary">
                {dashboardData?.unique_customers || 0}
              </div>
              <p className="text-xs text-muted-foreground">total unique customers</p>
            </CardContent>
          </BlurredCard>

          <BlurredCard>
            <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
              <CardTitle className="text-sm font-medium text-muted-foreground">Avg Order Value</CardTitle>
              <CreditCard className="h-4 w-4 text-muted-foreground" />
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold text-brand-secondary">
                {dashboardData ? formatCurrency(dashboardData.average_transaction_value) : formatCurrency(0)}
              </div>
              <p className="text-xs text-muted-foreground">per transaction</p>
            </CardContent>
          </BlurredCard>

          <BlurredCard>
            <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
              <CardTitle className="text-sm font-medium text-muted-foreground">Loyalty Engagement</CardTitle>
              <Target className="h-4 w-4 text-muted-foreground" />
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold text-warning">
                {loyaltyData?.total_members ? ((loyaltyData.total_members / (dashboardData?.total_customers || 1)) * 100).toFixed(1) : 0}%
              </div>
              <p className="text-xs text-muted-foreground">program engagement</p>
            </CardContent>
          </BlurredCard>
        </div>

        {/* Charts */}
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
          <BlurredCard>
            <CardHeader>
              <CardTitle className="text-foreground">Revenue Trends</CardTitle>
              <CardDescription className="text-muted-foreground">Monthly revenue and transaction volume</CardDescription>
            </CardHeader>
            <CardContent>
              {revenueLoading ? (
                <div className="h-[300px] flex items-center justify-center">
                  <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-primary"></div>
                </div>
              ) : (
                <RevenueChart data={revenueData?.daily_trend || []} />
              )}
            </CardContent>
          </BlurredCard>

          <BlurredCard>
            <CardHeader>
              <CardTitle className="text-foreground">Customer Growth</CardTitle>
              <CardDescription className="text-muted-foreground">New vs returning customers by month</CardDescription>
            </CardHeader>
            <CardContent>
              {customerLoading ? (
                <div className="h-[300px] flex items-center justify-center">
                  <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-primary"></div>
                </div>
              ) : (
                <CustomerChart data={customerData?.segments ? Object.entries(customerData.segments).map(([segment, data]) => ({
                  month: segment, // This needs to be adjusted if backend provides monthly data
                  new_customers: segment === 'new' ? data.count : 0,
                  returning_customers: segment !== 'new' ? data.count : 0,
                })) : []} />
              )}
            </CardContent>
          </BlurredCard>
        </div>

        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
          <BlurredCard>
            <CardHeader>
              <CardTitle className="text-foreground">Loyalty Program Distribution</CardTitle>
              <CardDescription className="text-muted-foreground">Customer distribution across loyalty tiers</CardDescription>
            </CardHeader>
            <CardContent>
              {loyaltyLoading ? (
                <div className="h-[300px] flex items-center justify-center">
                  <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-primary"></div>
                </div>
              ) : (
                <LoyaltyChart data={loyaltyData?.tier_distribution ? Object.entries(loyaltyData.tier_distribution).map(([tier, count]) => ({
                  name: tier,
                  value: count,
                  color: { "bronze": "#cd7f32", "silver": "#c0c0c0", "gold": "#ffd700", "platinum": "#e5e4e2" }[tier] || "#cccccc"
                })) : []} />
              )}
            </CardContent>
          </BlurredCard>

          <BlurredCard>
            <CardHeader>
              <CardTitle className="text-foreground">Performance Insights</CardTitle>
              <CardDescription className="text-muted-foreground">Key business insights and recommendations</CardDescription>
            </CardHeader>
            <CardContent>
              <div className="space-y-4">
                <div className="flex items-center justify-between p-3 bg-success/10 rounded-lg border border-success/20">
                  <div>
                    <p className="font-medium text-success">Revenue Growth</p>
                    <p className="text-sm text-muted-foreground">Strong month-over-month growth</p>
                  </div>
                  <Badge variant="default" className="bg-success/20 text-success hover:bg-success/30">
                    Excellent
                  </Badge>
                </div>

                <div className="flex items-center justify-between p-3 bg-warning/10 rounded-lg border border-warning/20">
                  <div>
                    <p className="font-medium text-warning">Customer Retention</p>
                    <p className="text-sm text-muted-foreground">Room for improvement in retention</p>
                  </div>
                  <Badge variant="secondary" className="bg-warning/20 text-warning hover:bg-warning/30">
                    Good
                  </Badge>
                </div>

                <div className="flex items-center justify-between p-3 bg-primary/10 rounded-lg border border-primary/20">
                  <div>
                    <p className="font-medium text-primary">Loyalty Engagement</p>
                    <p className="text-sm text-muted-foreground">High program participation</p>
                  </div>
                  <Badge variant="default" className="bg-primary/20 text-primary-foreground hover:bg-primary/30">
                    Great
                  </Badge>
                </div>
              </div>
            </CardContent>
          </BlurredCard>
        </div>
      </div>
    </DashboardLayout>
  )
}