"use client"

import { DashboardLayout } from "@/components/layout/dashboard-layout"
import { CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card"
import { Button } from "@/components/ui/button"
import { Badge } from "@/components/ui/badge"
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from "@/components/ui/table"
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select"
import { ArrowLeft, TrendingUp, DollarSign, Users, Activity, RefreshCw, Filter } from "lucide-react"
import Link from "next/link"
import { BlurredCard } from "@/components/blurred-card"

// Mock data - will be replaced with real API calls
const mockTransactions = [
  {
    id: "TXN001",
    timestamp: "2024-01-20T10:30:00Z",
    amount: 1500.00,
    customer_phone: "254712345678",
    customer_name: "John Doe",
    status: "completed",
    reference: "INV-2024-001",
    channel_id: 1,
    channel_name: "Main PayBill"
  },
  {
    id: "TXN002",
    timestamp: "2024-01-20T11:15:00Z",
    amount: 2500.00,
    customer_phone: "254723456789",
    customer_name: "Jane Smith",
    status: "completed",
    reference: "INV-2024-002",
    channel_id: 1,
    channel_name: "Main PayBill"
  },
  {
    id: "TXN003",
    timestamp: "2024-01-20T12:00:00Z",
    amount: 750.00,
    customer_phone: "254734567890",
    customer_name: "Bob Johnson",
    status: "failed",
    reference: "INV-2024-003",
    channel_id: 2,
    channel_name: "Test Channel"
  }
]

const mockAnalytics = {
  total_transactions: 156,
  total_volume: 234500.00,
  average_transaction: 1503.21,
  success_rate: 94.2,
  today_transactions: 23,
  today_volume: 34500.00,
  top_customers: [
    { phone: "254712345678", name: "John Doe", transactions: 12, total_spent: 18500.00 },
    { phone: "254723456789", name: "Jane Smith", transactions: 8, total_spent: 12200.00 },
    { phone: "254734567890", name: "Bob Johnson", transactions: 5, total_spent: 7500.00 }
  ]
}

const getStatusBadge = (status: string) => {
  switch (status) {
    case "completed":
      return <Badge variant="default" className="bg-green-100 text-green-800 border-green-200">Completed</Badge>
    case "failed":
      return <Badge variant="destructive">Failed</Badge>
    case "pending":
      return <Badge variant="secondary">Pending</Badge>
    default:
      return <Badge variant="outline">{status}</Badge>
  }
}

export default function TransactionAnalyticsPage() {
  return (
    <DashboardLayout>
      <div className="space-y-8">
        <div className="flex items-center justify-between">
          <div className="flex items-center space-x-4">
            <Link href="/dashboard/channels">
              <Button variant="ghost" size="sm" className="text-muted-foreground hover:bg-accent hover:text-foreground">
                <ArrowLeft className="h-4 w-4 mr-2" />
                Back to Channels
              </Button>
            </Link>
            <div>
              <h1 className="text-3xl font-bold text-foreground">Transaction Analytics</h1>
              <p className="text-muted-foreground mt-1">Monitor and analyze your M-Pesa transactions</p>
            </div>
          </div>
          <div className="flex items-center space-x-2">
            <Select defaultValue="all">
              <SelectTrigger className="w-[180px]">
                <SelectValue placeholder="Filter by channel" />
              </SelectTrigger>
              <SelectContent>
                <SelectItem value="all">All Channels</SelectItem>
                <SelectItem value="1">Main PayBill</SelectItem>
                <SelectItem value="2">Test Channel</SelectItem>
              </SelectContent>
            </Select>
            <Button variant="outline" size="sm">
              <RefreshCw className="h-4 w-4 mr-2" />
              Refresh
            </Button>
          </div>
        </div>

        {/* Analytics Overview */}
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
          <BlurredCard>
            <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
              <CardTitle className="text-sm font-medium text-muted-foreground">Total Transactions</CardTitle>
              <Activity className="h-4 w-4 text-muted-foreground" />
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold text-foreground">{mockAnalytics.total_transactions}</div>
              <p className="text-xs text-muted-foreground">
                +12% from last month
              </p>
            </CardContent>
          </BlurredCard>

          <BlurredCard>
            <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
              <CardTitle className="text-sm font-medium text-muted-foreground">Total Volume</CardTitle>
              <DollarSign className="h-4 w-4 text-muted-foreground" />
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold text-foreground">KES {mockAnalytics.total_volume.toLocaleString()}</div>
              <p className="text-xs text-muted-foreground">
                +8% from last month
              </p>
            </CardContent>
          </BlurredCard>

          <BlurredCard>
            <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
              <CardTitle className="text-sm font-medium text-muted-foreground">Average Transaction</CardTitle>
              <TrendingUp className="h-4 w-4 text-muted-foreground" />
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold text-foreground">KES {mockAnalytics.average_transaction.toLocaleString()}</div>
              <p className="text-xs text-muted-foreground">
                +5% from last month
              </p>
            </CardContent>
          </BlurredCard>

          <BlurredCard>
            <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
              <CardTitle className="text-sm font-medium text-muted-foreground">Success Rate</CardTitle>
              <Users className="h-4 w-4 text-muted-foreground" />
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold text-foreground">{mockAnalytics.success_rate}%</div>
              <p className="text-xs text-muted-foreground">
                +2% from last month
              </p>
            </CardContent>
          </BlurredCard>
        </div>

        <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
          {/* Recent Transactions */}
          <BlurredCard>
            <CardHeader>
              <CardTitle className="text-foreground">Recent Transactions</CardTitle>
              <CardDescription className="text-muted-foreground">
                Latest M-Pesa transactions across all channels
              </CardDescription>
            </CardHeader>
            <CardContent>
              <Table>
                <TableHeader>
                  <TableRow>
                    <TableHead>Transaction ID</TableHead>
                    <TableHead>Amount</TableHead>
                    <TableHead>Customer</TableHead>
                    <TableHead>Status</TableHead>
                    <TableHead>Channel</TableHead>
                  </TableRow>
                </TableHeader>
                <TableBody>
                  {mockTransactions.map((transaction) => (
                    <TableRow key={transaction.id}>
                      <TableCell className="font-medium font-mono text-sm">
                        {transaction.id}
                      </TableCell>
                      <TableCell className="font-medium">
                        KES {transaction.amount.toLocaleString()}
                      </TableCell>
                      <TableCell>
                        <div>
                          <p className="font-medium">{transaction.customer_name}</p>
                          <p className="text-sm text-muted-foreground">{transaction.customer_phone}</p>
                        </div>
                      </TableCell>
                      <TableCell>{getStatusBadge(transaction.status)}</TableCell>
                      <TableCell>
                        <Badge variant="outline">{transaction.channel_name}</Badge>
                      </TableCell>
                    </TableRow>
                  ))}
                </TableBody>
              </Table>
            </CardContent>
          </BlurredCard>

          {/* Top Customers */}
          <BlurredCard>
            <CardHeader>
              <CardTitle className="text-foreground">Top Customers</CardTitle>
              <CardDescription className="text-muted-foreground">
                Your most active customers by transaction volume
              </CardDescription>
            </CardHeader>
            <CardContent>
              <div className="space-y-4">
                {mockAnalytics.top_customers.map((customer, index) => (
                  <div key={customer.phone} className="flex items-center justify-between p-3 bg-muted/30 rounded-lg">
                    <div className="flex items-center space-x-3">
                      <div className="w-8 h-8 bg-primary/10 rounded-full flex items-center justify-center text-sm font-medium text-primary">
                        {index + 1}
                      </div>
                      <div>
                        <p className="font-medium text-foreground">{customer.name}</p>
                        <p className="text-sm text-muted-foreground">{customer.phone}</p>
                      </div>
                    </div>
                    <div className="text-right">
                      <p className="font-medium text-foreground">{customer.transactions} txns</p>
                      <p className="text-sm text-muted-foreground">KES {customer.total_spent.toLocaleString()}</p>
                    </div>
                  </div>
                ))}
              </div>
            </CardContent>
          </BlurredCard>
        </div>

        {/* Today's Summary */}
        <BlurredCard>
          <CardHeader>
            <CardTitle className="text-foreground">Today's Summary</CardTitle>
            <CardDescription className="text-muted-foreground">
              Transaction activity for today
            </CardDescription>
          </CardHeader>
          <CardContent>
            <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
              <div className="text-center">
                <div className="text-2xl font-bold text-foreground">{mockAnalytics.today_transactions}</div>
                <p className="text-sm text-muted-foreground">Transactions Today</p>
              </div>
              <div className="text-center">
                <div className="text-2xl font-bold text-foreground">KES {mockAnalytics.today_volume.toLocaleString()}</div>
                <p className="text-sm text-muted-foreground">Volume Today</p>
              </div>
              <div className="text-center">
                <div className="text-2xl font-bold text-foreground">
                  {mockAnalytics.today_transactions > 0
                    ? (mockAnalytics.today_volume / mockAnalytics.today_transactions).toFixed(0)
                    : "0"
                  }
                </div>
                <p className="text-sm text-muted-foreground">Avg Transaction</p>
              </div>
            </div>
          </CardContent>
        </BlurredCard>
      </div>
    </DashboardLayout>
  )
}
