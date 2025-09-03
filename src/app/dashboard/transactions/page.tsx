"use client"

import { useState } from "react"
import { DashboardLayout } from "@/components/layout/dashboard-layout"
import { CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card"
import { Button } from "@/components/ui/button"
import { Input } from "@/components/ui/input"
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from "@/components/ui/table"
import { Badge } from "@/components/ui/badge"
import { useTransactions } from "@/hooks/use-api"
import { formatCurrency, formatDateTime } from "@/lib/utils"
import { Search, Download, RefreshCw } from "lucide-react"
import { apiService } from "@/services/api-service"
import { useAuth } from "@/contexts/auth-context"
import { BlurredCard } from "@/components/blurred-card"

export default function TransactionsPage() {
  const [page, setPage] = useState(1)
  const [searchTerm, setSearchTerm] = useState("")
  const [syncing, setSyncing] = useState(false)
  const { user } = useAuth()

  const { data, error, isLoading, mutate } = useTransactions({ page, limit: 20 })

  const transactions = data?.transactions || []
  const total = data?.total || 0

  const handleSyncTransactions = async () => {
    if (!user?.merchant_id) return

    setSyncing(true)
    try {
      await apiService.syncTransactions(user.merchant_id)
      mutate() // Refresh the data
    } catch (error) {
      console.error("Failed to sync transactions:", error)
    } finally {
      setSyncing(false)
    }
  }

  if (error) {
    return (
      <DashboardLayout>
        <div className="flex items-center justify-center h-64">
          <p className="text-destructive">Error loading transactions. Please try again.</p>
        </div>
      </DashboardLayout>
    )
  }

  return (
    <DashboardLayout>
      <div className="space-y-8">
        <div className="flex items-center justify-between">
          <div>
            <h1 className="text-3xl font-bold text-foreground">Transactions</h1>
            <p className="text-muted-foreground mt-1">Monitor all customer transactions and payments</p>
          </div>
          <div className="flex space-x-2">
            <Button variant="outline" onClick={handleSyncTransactions} disabled={syncing} className="bg-background/50 border-border text-foreground hover:bg-accent">
              <RefreshCw className={`h-4 w-4 mr-2 ${syncing ? "animate-spin" : ""}`} />
              {syncing ? "Syncing..." : "Sync from Daraja"}
            </Button>
            <Button variant="outline" className="bg-background/50 border-border text-foreground hover:bg-accent">
              <Download className="h-4 w-4 mr-2" />
              Export
            </Button>
          </div>
        </div>

        <BlurredCard>
          <CardHeader>
            <CardTitle className="text-foreground">Transaction History</CardTitle>
            <CardDescription className="text-muted-foreground">All transactions processed through your business</CardDescription>
          </CardHeader>
          <CardContent>
            <div className="flex items-center space-x-4 mb-6">
              <div className="relative flex-1 max-w-sm">
                <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 text-muted-foreground h-4 w-4" />
                <Input
                  placeholder="Search transactions..."
                  value={searchTerm}
                  onChange={(e) => setSearchTerm(e.target.value)}
                  className="pl-10 bg-background/50 border-border focus:border-primary"
                />
              </div>
            </div>

            {isLoading ? (
              <div className="flex items-center justify-center h-32">
                <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-primary"></div>
              </div>
            ) : (
              <Table>
                <TableHeader>
                  <TableRow>
                    <TableHead>Transaction ID</TableHead>
                    <TableHead>Date & Time</TableHead>
                    <TableHead>Customer</TableHead>
                    <TableHead>Amount</TableHead>
                    <TableHead>Status</TableHead>
                    <TableHead>Description</TableHead>
                  </TableRow>
                </TableHeader>
                <TableBody>
                  {transactions.map((transaction) => (
                    <TableRow key={transaction.id}>
                      <TableCell className="font-mono text-sm text-foreground">{transaction.id.slice(0, 8)}...</TableCell>
                      <TableCell className="text-muted-foreground">{formatDateTime(transaction.transaction_date)}</TableCell>
                      <TableCell className="text-foreground">{transaction.customer_id}</TableCell>
                      <TableCell className="font-medium text-foreground">
                        {formatCurrency(transaction.amount)} {transaction.currency}
                      </TableCell>
                      <TableCell>
                        <Badge
                          variant={
                            transaction.status === "completed"
                              ? "default"
                              : transaction.status === "pending"
                                ? "secondary"
                                : "destructive"
                          }
                        >
                          {transaction.status}
                        </Badge>
                      </TableCell>
                      <TableCell className="max-w-xs truncate text-muted-foreground">{transaction.description || "No description"}</TableCell>
                    </TableRow>
                  ))}
                </TableBody>
              </Table>
            )}

            {transactions.length === 0 && !isLoading && (
              <div className="text-center py-8">
                <p className="text-muted-foreground mb-4">No transactions found</p>
                <Button
                  variant="outline"
                  className="mt-4 bg-background/50 border-border text-foreground hover:bg-accent"
                  onClick={handleSyncTransactions}
                  disabled={syncing}
                >
                  <RefreshCw className={`h-4 w-4 mr-2 ${syncing ? "animate-spin" : ""}`} />
                  Sync Transactions
                </Button>
              </div>
            )}

            {total > 20 && (
              <div className="flex items-center justify-between mt-6">
                <p className="text-sm text-muted-foreground">
                  Showing {(page - 1) * 20 + 1} to {Math.min(page * 20, total)} of {total} transactions
                </p>
                <div className="flex space-x-2">
                  <Button variant="outline" size="sm" disabled={page === 1} onClick={() => setPage(page - 1)} className="bg-background/50 border-border text-foreground hover:bg-accent">
                    Previous
                  </Button>
                  <Button variant="outline" size="sm" disabled={page * 20 >= total} onClick={() => setPage(page + 1)} className="bg-background/50 border-border text-foreground hover:bg-accent">
                    Next
                  </Button>
                </div>
              </div>
            )}
          </CardContent>
        </BlurredCard>
      </div>
    </DashboardLayout>
  )
}