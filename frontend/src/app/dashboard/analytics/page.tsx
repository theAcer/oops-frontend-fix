"use client"

import { DashboardLayout } from "@/components/layout/dashboard-layout"
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card"
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

export default function AnalyticsPage() {
  const { data: dashboardData, isLoading: dashboardLoading } = useDashboardAnalytics()
  const { data: revenueData, isLoading: revenueLoading } = useRevenueAnalytics()
  const { data: customerData, isLoading: customerLoading } = useCustomerAnalytics()
  const { data: loyaltyData, isLoading: loyaltyLoading } = useLoyaltyAnalytics()
  const { data: realTimeData, isLoading: realTimeLoading } = useRealTimeMetrics()

  // Mock data for charts (replace with real data from API)
  const revenueChartData = [
    { date: "Jan", revenue: 45000, transactions: 120 },
    { date: "Feb", revenue: 52000, transactions: 140 },
    { date: "Mar", revenue: 48000, transactions: 130 },
    { date: "Apr", revenue: 61000, transactions: 165 },
    { date: "May", revenue: 55000, transactions: 150 },
    { date: "Jun", revenue: 67000, transactions: 180 },
  ]

  const customerChartData = [
    { month: "Jan", new_customers: 45, returning_customers: 75 },
    { month: "Feb", new_customers: 52, returning_customers: 88 },
    { month: "Mar", new_customers: 48, returning_customers: 82 },
    { month: "Apr", new_customers: 61, returning_customers: 104 },
    { month: "May", new_customers: 55, returning_customers: 95 },
    { month: "Jun", new_customers: 67, returning_customers: 113 },
  ]

  const loyaltyChartData = [
    { name: "Bronze", value: 45, color: "#cd7f32" },
    { name: "Silver", value: 30, color: "#c0c0c0" },
    { name: "Gold", value: 20, color: "#ffd700" },
    { name: "Platinum", value: 5, color: "#e5e4e2" },
  ]

  return (
    <DashboardLayout>
      <div className="space-y-6">
        <div className="flex items-center justify-between">
          <div>
            <h1 className="text-3xl font-bold text-gray-900">Analytics</h1>
            <p className="text-gray-600">Comprehensive business insights and performance metrics</p>
          </div>
          <Button variant="outline">
            <Clock className="h-4 w-4 mr-2" />
            Real-time View
          </Button>
        </div>

        {/* Real-time Metrics */}
        <Card>
          <CardHeader>
            <CardTitle className="flex items-center space-x-2">
              <Clock className="h-5 w-5" />
              <span>Today's Performance</span>
            </CardTitle>
            <CardDescription>Live metrics updated every 10 seconds</CardDescription>
          </CardHeader>
          <CardContent>
            {realTimeLoading ? (
              <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
                {[...Array(4)].map((_, i) => (
                  <div key={i} className="animate-pulse">
                    <div className="h-4 bg-gray-200 rounded w-1/2 mb-2"></div>
                    <div className="h-8 bg-gray-200 rounded w-3/4"></div>
                  </div>
                ))}
              </div>
            ) : (
              <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
                <div className="text-center">
                  <p className="text-sm text-gray-600">Today's Revenue</p>
                  <p className="text-2xl font-bold text-green-600">
                    {realTimeData ? formatCurrency(realTimeData.today_revenue || 0) : formatCurrency(0)}
                  </p>
                </div>
                <div className="text-center">
                  <p className="text-sm text-gray-600">Today's Transactions</p>
                  <p className="text-2xl font-bold text-blue-600">{realTimeData?.today_transactions || 0}</p>
                </div>
                <div className="text-center">
                  <p className="text-sm text-gray-600">New Customers</p>
                  <p className="text-2xl font-bold text-purple-600">{realTimeData?.today_new_customers || 0}</p>
                </div>
                <div className="text-center">
                  <p className="text-sm text-gray-600">Active Sessions</p>
                  <p className="text-2xl font-bold text-orange-600">{realTimeData?.active_sessions || 0}</p>
                </div>
              </div>
            )}
          </CardContent>
        </Card>

        {/* Key Metrics */}
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
          <Card>
            <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
              <CardTitle className="text-sm font-medium">Revenue Growth</CardTitle>
              <TrendingUp className="h-4 w-4 text-muted-foreground" />
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold text-green-600">
                +{dashboardData?.revenue_growth?.toFixed(1) || 0}%
              </div>
              <p className="text-xs text-muted-foreground">vs last month</p>
            </CardContent>
          </Card>

          <Card>
            <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
              <CardTitle className="text-sm font-medium">Customer Retention</CardTitle>
              <Users className="h-4 w-4 text-muted-foreground" />
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold text-blue-600">
                {dashboardData?.customer_retention_rate?.toFixed(1) || 0}%
              </div>
              <p className="text-xs text-muted-foreground">retention rate</p>
            </CardContent>
          </Card>

          <Card>
            <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
              <CardTitle className="text-sm font-medium">Avg Order Value</CardTitle>
              <CreditCard className="h-4 w-4 text-muted-foreground" />
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold text-purple-600">
                {dashboardData ? formatCurrency(dashboardData.average_order_value) : formatCurrency(0)}
              </div>
              <p className="text-xs text-muted-foreground">per transaction</p>
            </CardContent>
          </Card>

          <Card>
            <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
              <CardTitle className="text-sm font-medium">Loyalty Engagement</CardTitle>
              <Target className="h-4 w-4 text-muted-foreground" />
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold text-orange-600">
                {dashboardData?.loyalty_program_engagement?.toFixed(1) || 0}%
              </div>
              <p className="text-xs text-muted-foreground">program engagement</p>
            </CardContent>
          </Card>
        </div>

        {/* Charts */}
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
          <Card>
            <CardHeader>
              <CardTitle>Revenue Trends</CardTitle>
              <CardDescription>Monthly revenue and transaction volume</CardDescription>
            </CardHeader>
            <CardContent>
              {revenueLoading ? (
                <div className="h-[300px] flex items-center justify-center">
                  <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-primary"></div>
                </div>
              ) : (
                <RevenueChart data={revenueChartData} />
              )}
            </CardContent>
          </Card>

          <Card>
            <CardHeader>
              <CardTitle>Customer Growth</CardTitle>
              <CardDescription>New vs returning customers by month</CardDescription>
            </CardHeader>
            <CardContent>
              {customerLoading ? (
                <div className="h-[300px] flex items-center justify-center">
                  <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-primary"></div>
                </div>
              ) : (
                <CustomerChart data={customerChartData} />
              )}
            </CardContent>
          </Card>
        </div>

        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
          <Card>
            <CardHeader>
              <CardTitle>Loyalty Program Distribution</CardTitle>
              <CardDescription>Customer distribution across loyalty tiers</CardDescription>
            </CardHeader>
            <CardContent>
              {loyaltyLoading ? (
                <div className="h-[300px] flex items-center justify-center">
                  <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-primary"></div>
                </div>
              ) : (
                <LoyaltyChart data={loyaltyChartData} />
              )}
            </CardContent>
          </Card>

          <Card>
            <CardHeader>
              <CardTitle>Performance Insights</CardTitle>
              <CardDescription>Key business insights and recommendations</CardDescription>
            </CardHeader>
            <CardContent>
              <div className="space-y-4">
                <div className="flex items-center justify-between p-3 bg-green-50 rounded-lg">
                  <div>
                    <p className="font-medium text-green-800">Revenue Growth</p>
                    <p className="text-sm text-green-600">Strong month-over-month growth</p>
                  </div>
                  <Badge variant="default" className="bg-green-100 text-green-800">
                    Excellent
                  </Badge>
                </div>

                <div className="flex items-center justify-between p-3 bg-yellow-50 rounded-lg">
                  <div>
                    <p className="font-medium text-yellow-800">Customer Retention</p>
                    <p className="text-sm text-yellow-600">Room for improvement in retention</p>
                  </div>
                  <Badge variant="secondary" className="bg-yellow-100 text-yellow-800">
                    Good
                  </Badge>
                </div>

                <div className="flex items-center justify-between p-3 bg-blue-50 rounded-lg">
                  <div>
                    <p className="font-medium text-blue-800">Loyalty Engagement</p>
                    <p className="text-sm text-blue-600">High program participation</p>
                  </div>
                  <Badge variant="default" className="bg-blue-100 text-blue-800">
                    Great
                  </Badge>
                </div>
              </div>
            </CardContent>
          </Card>
        </div>
      </div>
    </DashboardLayout>
  )
}
