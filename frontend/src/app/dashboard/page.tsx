"use client"

import { DashboardLayout } from "@/components/layout/dashboard-layout"
import { CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card"
import { Button } from "@/components/ui/button"
import { useDashboardAnalytics, useTransactions } from "@/hooks/use-api"
import { formatCurrency } from "@/lib/utils"
import { BarChart3, Users, CreditCard, TrendingUp, ArrowUpRight, ArrowDownRight } from "lucide-react"
import Link from "next/link"
import { BlurredCard } from "@/components/blurred-card"

export default function DashboardPage() {
  const { data: analytics, error: analyticsError, isLoading: analyticsLoading } = useDashboardAnalytics()
  const { data: recentTransactions, isLoading: transactionsLoading } = useTransactions({ limit: 5 })

  const transactions = recentTransactions?.transactions || []

  return (
    <DashboardLayout>
      <div className="space-y-8">
        <div>
          <h1 className="text-3xl font-bold text-foreground">Dashboard</h1>
          <p className="text-muted-foreground mt-1">Overview of your business performance</p>
        </div>

        {analyticsLoading ? (
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
            {[...Array(4)].map((_, i) => (
              <BlurredCard key={i}>
                <CardContent className="p-6">
                  <div className="animate-pulse">
                    <div className="h-4 bg-muted rounded w-1/2 mb-2"></div>
                    <div className="h-8 bg-muted rounded w-3/4 mb-1"></div>
                    <div className="h-3 bg-muted rounded w-1/3"></div>
                  </div>
                </CardContent>
              </BlurredCard>
            ))}
          </div>
        ) : analyticsError ? (
          <BlurredCard>
            <CardContent className="p-6">
              <p className="text-destructive">Error loading analytics. Please try again.</p>
            </CardContent>
          </BlurredCard>
        ) : (
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
            <BlurredCard>
              <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
                <CardTitle className="text-sm font-medium text-muted-foreground">Total Revenue</CardTitle>
                <CreditCard className="h-4 w-4 text-muted-foreground" />
              </CardHeader>
              <CardContent>
                <div className="text-2xl font-bold text-foreground">
                  {analytics?.overview?.total_revenue ? formatCurrency(analytics.overview.total_revenue) : formatCurrency(0)}
                </div>
                <p className="text-xs text-muted-foreground flex items-center mt-1">
                  {analytics?.overview?.growth_metrics?.revenue_growth && analytics.overview.growth_metrics.revenue_growth > 0 ? (
                    <ArrowUpRight className="h-3 w-3 text-success mr-1" />
                  ) : (
                    <ArrowDownRight className="h-3 w-3 text-destructive mr-1" />
                  )}
                  {analytics?.overview?.growth_metrics?.revenue_growth ? `${analytics.overview.growth_metrics.revenue_growth.toFixed(1)}%` : "0%"} from last month
                </p>
              </CardContent>
            </BlurredCard>

            <BlurredCard>
              <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
                <CardTitle className="text-sm font-medium text-muted-foreground">Total Customers</CardTitle>
                <Users className="h-4 w-4 text-muted-foreground" />
              </CardHeader>
              <CardContent>
                <div className="text-2xl font-bold text-foreground">{analytics?.overview?.total_customers || 0}</div>
                <p className="text-xs text-muted-foreground flex items-center mt-1">
                  {analytics?.overview?.growth_metrics?.customer_growth && analytics.overview.growth_metrics.customer_growth > 0 ? (
                    <ArrowUpRight className="h-3 w-3 text-success mr-1" />
                  ) : (
                    <ArrowDownRight className="h-3 w-3 text-destructive mr-1" />
                  )}
                  {analytics?.overview?.growth_metrics?.customer_growth ? `${analytics.overview.growth_metrics.customer_growth.toFixed(1)}%` : "0%"} from last month
                </p>
              </CardContent>
            </BlurredCard>

            <BlurredCard>
              <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
                <CardTitle className="text-sm font-medium text-muted-foreground">Total Transactions</CardTitle>
                <BarChart3 className="h-4 w-4 text-muted-foreground" />
              </CardHeader>
              <CardContent>
                <div className="text-2xl font-bold text-foreground">{analytics?.overview?.total_transactions || 0}</div>
                <p className="text-xs text-muted-foreground mt-1">Processed this month</p>
              </CardContent>
            </BlurredCard>

            <BlurredCard>
              <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
                <CardTitle className="text-sm font-medium text-muted-foreground">Avg Order Value</CardTitle>
                <TrendingUp className="h-4 w-4 text-muted-foreground" />
              </CardHeader>
              <CardContent>
                <div className="text-2xl font-bold text-foreground">
                  {analytics?.overview?.average_transaction_value ? formatCurrency(analytics.overview.average_transaction_value) : formatCurrency(0)}
                </div>
                <p className="text-xs text-muted-foreground mt-1">Per transaction</p>
              </CardContent>
            </BlurredCard>
          </div>
        )}

        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
          <BlurredCard>
            <CardHeader>
              <CardTitle className="text-foreground">Recent Transactions</CardTitle>
              <CardDescription className="text-muted-foreground">Latest customer transactions</CardDescription>
            </CardHeader>
            <CardContent>
              {transactionsLoading ? (
                <div className="space-y-4">
                  {[...Array(3)].map((_, i) => (
                    <div key={i} className="animate-pulse flex items-center space-x-4">
                      <div className="w-2 h-2 bg-muted rounded-full"></div>
                      <div className="flex-1">
                        <div className="h-4 bg-muted rounded w-3/4 mb-1"></div>
                        <div className="h-3 bg-muted rounded w-1/2"></div>
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
                          transaction.status === "completed" ? "bg-success" : "bg-warning"
                        }`}
                      ></div>
                      <div className="flex-1">
                        <p className="text-sm font-medium text-foreground">{formatCurrency(transaction.amount)}</p>
                        <p className="text-xs text-muted-foreground">
                          {new Date(transaction.transaction_date).toLocaleString()}
                        </p>
                      </div>
                    </div>
                  ))}
                </div>
              ) : (
                <p className="text-muted-foreground text-center py-4">No recent transactions</p>
              )}
              <div className="mt-6">
                <Link href="/dashboard/transactions">
                  <Button variant="outline" size="sm" className="w-full bg-background/50 border-border text-foreground hover:bg-accent">
                    View All Transactions
                  </Button>
                </Link>
              </div>
            </CardContent>
          </BlurredCard>

          <BlurredCard>
            <CardHeader>
              <CardTitle className="text-foreground">Quick Actions</CardTitle>
              <CardDescription className="text-muted-foreground">Common tasks and shortcuts</CardDescription>
            </CardHeader>
            <CardContent>
              <div className="grid grid-cols-2 gap-4">
                <Link href="/dashboard/campaigns">
                  <button className="p-4 text-left border border-border/50 rounded-lg bg-background/50 hover:bg-accent transition-colors w-full">
                    <div className="font-medium text-foreground">Send Campaign</div>
                    <div className="text-sm text-muted-foreground">Create marketing campaign</div>
                  </button>
                </Link>
                <Link href="/dashboard/analytics">
                  <button className="p-4 text-left border border-border/50 rounded-lg bg-background/50 hover:bg-accent transition-colors w-full">
                    <div className="font-medium text-foreground">View Analytics</div>
                    <div className="text-sm text-muted-foreground">Detailed insights</div>
                  </button>
                </Link>
                <Link href="/dashboard/loyalty">
                  <button className="p-4 text-left border border-border/50 rounded-lg bg-background/50 hover:bg-accent transition-colors w-full">
                    <div className="font-medium text-foreground">Manage Loyalty</div>
                    <div className="text-sm text-muted-foreground">Update programs</div>
                  </button>
                </Link>
                <Link href="/dashboard/ai-insights">
                  <button className="p-4 text-left border border-border/50 rounded-lg bg-background/50 hover:bg-accent transition-colors w-full">
                    <div className="font-medium text-foreground">AI Insights</div>
                    <div className="text-sm text-muted-foreground">Customer predictions</div>
                  </button>
                </Link>
              </div>
            </CardContent>
          </BlurredCard>
        </div>
      </div>
    </DashboardLayout>
  )
}