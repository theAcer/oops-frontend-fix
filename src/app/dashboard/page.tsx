"use client"

import { DashboardLayout } from "@/components/layout/dashboard-layout"
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card"
import { Button } from "@/components/ui/button"
import { useDashboardAnalytics, useTransactions } from "@/hooks/use-api"
import { formatCurrency } from "@/lib/utils"
import { BarChart3, Users, CreditCard, TrendingUp, ArrowUpRight, ArrowDownRight } from "lucide-react"
import Link from "next/link"

export default function DashboardPage() {
  const { data: analytics, error: analyticsError, isLoading: analyticsLoading } = useDashboardAnalytics()
  const { data: recentTransactions, isLoading: transactionsLoading } = useTransactions({ limit: 5 })

  const transactions = recentTransactions?.transactions || []

  return (
    <DashboardLayout>
      <div className="space-y-6">
        <div>
          <h1 className="text-3xl font-bold text-gray-900">Dashboard</h1>
          <p className="text-gray-600">Overview of your business performance</p>
        </div>

        {analyticsLoading ? (
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
            {[...Array(4)].map((_, i) => (
              <Card key={i}>
                <CardContent className="p-6">
                  <div className="animate-pulse">
                    <div className="h-4 bg-gray-200 rounded w-1/2 mb-2"></div>
                    <div className="h-8 bg-gray-200 rounded w-3/4 mb-1"></div>
                    <div className="h-3 bg-gray-200 rounded w-1/3"></div>
                  </div>
                </CardContent>
              </Card>
            ))}
          </div>
        ) : analyticsError ? (
          <Card>
            <CardContent className="p-6">
              <p className="text-red-600">Error loading analytics. Please try again.</p>
            </CardContent>
          </Card>
        ) : (
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
            <Card>
              <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
                <CardTitle className="text-sm font-medium">Total Revenue</CardTitle>
                <CreditCard className="h-4 w-4 text-muted-foreground" />
              </CardHeader>
              <CardContent>
                <div className="text-2xl font-bold">
                  {analytics ? formatCurrency(analytics.total_revenue) : formatCurrency(0)}
                </div>
                <p className="text-xs text-muted-foreground flex items-center">
                  {analytics && analytics.revenue_growth > 0 ? (
                    <ArrowUpRight className="h-3 w-3 text-green-500 mr-1" />
                  ) : (
                    <ArrowDownRight className="h-3 w-3 text-red-500 mr-1" />
                  )}
                  {analytics ? `${analytics.revenue_growth.toFixed(1)}%` : "0%"} from last month
                </p>
              </CardContent>
            </Card>

            <Card>
              <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
                <CardTitle className="text-sm font-medium">Total Customers</CardTitle>
                <Users className="h-4 w-4 text-muted-foreground" />
              </CardHeader>
              <CardContent>
                <div className="text-2xl font-bold">{analytics?.total_customers || 0}</div>
                <p className="text-xs text-muted-foreground flex items-center">
                  {analytics && analytics.customer_growth > 0 ? (
                    <ArrowUpRight className="h-3 w-3 text-green-500 mr-1" />
                  ) : (
                    <ArrowDownRight className="h-3 w-3 text-red-500 mr-1" />
                  )}
                  {analytics ? `${analytics.customer_growth.toFixed(1)}%` : "0%"} from last month
                </p>
              </CardContent>
            </Card>

            <Card>
              <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
                <CardTitle className="text-sm font-medium">Total Transactions</CardTitle>
                <BarChart3 className="h-4 w-4 text-muted-foreground" />
              </CardHeader>
              <CardContent>
                <div className="text-2xl font-bold">{analytics?.total_transactions || 0}</div>
                <p className="text-xs text-muted-foreground">Processed this month</p>
              </CardContent>
            </Card>

            <Card>
              <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
                <CardTitle className="text-sm font-medium">Avg Order Value</CardTitle>
                <TrendingUp className="h-4 w-4 text-muted-foreground" />
              </CardHeader>
              <CardContent>
                <div className="text-2xl font-bold">
                  {analytics ? formatCurrency(analytics.average_order_value) : formatCurrency(0)}
                </div>
                <p className="text-xs text-muted-foreground">Per transaction</p>
              </CardContent>
            </Card>
          </div>
        )}

        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
          <Card>
            <CardHeader>
              <CardTitle>Recent Transactions</CardTitle>
              <CardDescription>Latest customer transactions</CardDescription>
            </CardHeader>
            <CardContent>
              {transactionsLoading ? (
                <div className="space-y-4">
                  {[...Array(3)].map((_, i) => (
                    <div key={i} className="animate-pulse flex items-center space-x-4">
                      <div className="w-2 h-2 bg-gray-200 rounded-full"></div>
                      <div className="flex-1">
                        <div className="h-4 bg-gray-200 rounded w-3/4 mb-1"></div>
                        <div className="h-3 bg-gray-200 rounded w-1/2"></div>
                      </div>
                    </div>
                  ))}
                </div>
              ) : transactions.length > 0 ? (
                <div className="space-y-4">
                  {transactions.map((transaction) => (
                    <div key={transaction.id} className="flex items-center space-x-4">
                      <div
                        className={`w-2 h-2 rounded-full ${
                          transaction.status === "completed" ? "bg-green-500" : "bg-yellow-500"
                        }`}
                      ></div>
                      <div className="flex-1">
                        <p className="text-sm font-medium">{formatCurrency(transaction.amount)}</p>
                        <p className="text-xs text-muted-foreground">
                          {new Date(transaction.transaction_date).toLocaleString()}
                        </p>
                      </div>
                    </div>
                  ))}
                </div>
              ) : (
                <p className="text-gray-500 text-center py-4">No recent transactions</p>
              )}
              <div className="mt-4">
                <Link href="/dashboard/transactions">
                  <Button variant="outline" size="sm" className="w-full bg-transparent">
                    View All Transactions
                  </Button>
                </Link>
              </div>
            </CardContent>
          </Card>

          <Card>
            <CardHeader>
              <CardTitle>Quick Actions</CardTitle>
              <CardDescription>Common tasks and shortcuts</CardDescription>
            </CardHeader>
            <CardContent>
              <div className="grid grid-cols-2 gap-4">
                <Link href="/dashboard/campaigns">
                  <button className="p-4 text-left border rounded-lg hover:bg-gray-50 transition-colors w-full">
                    <div className="font-medium">Send Campaign</div>
                    <div className="text-sm text-muted-foreground">Create marketing campaign</div>
                  </button>
                </Link>
                <Link href="/dashboard/analytics">
                  <button className="p-4 text-left border rounded-lg hover:bg-gray-50 transition-colors w-full">
                    <div className="font-medium">View Analytics</div>
                    <div className="text-sm text-muted-foreground">Detailed insights</div>
                  </button>
                </Link>
                <Link href="/dashboard/loyalty">
                  <button className="p-4 text-left border rounded-lg hover:bg-gray-50 transition-colors w-full">
                    <div className="font-medium">Manage Loyalty</div>
                    <div className="text-sm text-muted-foreground">Update programs</div>
                  </button>
                </Link>
                <Link href="/dashboard/ai-insights">
                  <button className="p-4 text-left border rounded-lg hover:bg-gray-50 transition-colors w-full">
                    <div className="font-medium">AI Insights</div>
                    <div className="text-sm text-muted-foreground">Customer predictions</div>
                  </button>
                </Link>
              </div>
            </CardContent>
          </Card>
        </div>
      </div>
    </DashboardLayout>
  )
}
