"use client"

import { useParams } from "next/navigation"
import { DashboardLayout } from "@/components/layout/dashboard-layout"
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card"
import { Button } from "@/components/ui/button"
import { Badge } from "@/components/ui/badge"
import { useCustomer, useTransactions } from "@/hooks/use-api"
import { formatCurrency, formatDate, formatDateTime } from "@/lib/utils"
import { ArrowLeft, Mail, Phone, Calendar, CreditCard, Gift } from "lucide-react"
import Link from "next/link"

export default function CustomerDetailPage() {
  const params = useParams()
  const customerId = params.id as string

  const { data: customer, error: customerError, isLoading: customerLoading } = useCustomer(customerId)
  const {
    data: transactionsData,
    error: transactionsError,
    isLoading: transactionsLoading,
  } = useTransactions({ customer_id: customerId, limit: 5 })

  const transactions = transactionsData?.transactions || []

  if (customerError || transactionsError) {
    return (
      <DashboardLayout>
        <div className="flex items-center justify-center h-64">
          <p className="text-red-600">Error loading customer data. Please try again.</p>
        </div>
      </DashboardLayout>
    )
  }

  if (customerLoading) {
    return (
      <DashboardLayout>
        <div className="flex items-center justify-center h-64">
          <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-primary"></div>
        </div>
      </DashboardLayout>
    )
  }

  if (!customer) {
    return (
      <DashboardLayout>
        <div className="flex items-center justify-center h-64">
          <p className="text-gray-600">Customer not found</p>
        </div>
      </DashboardLayout>
    )
  }

  return (
    <DashboardLayout>
      <div className="space-y-6">
        <div className="flex items-center space-x-4">
          <Link href="/dashboard/customers">
            <Button variant="ghost" size="sm">
              <ArrowLeft className="h-4 w-4 mr-2" />
              Back to Customers
            </Button>
          </Link>
        </div>

        <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
          <div className="lg:col-span-2 space-y-6">
            <Card>
              <CardHeader>
                <div className="flex items-center justify-between">
                  <div>
                    <CardTitle className="text-2xl">{customer.name}</CardTitle>
                    <CardDescription>Customer since {formatDate(customer.created_at)}</CardDescription>
                  </div>
                  <Badge variant={customer.loyalty_points > 1000 ? "default" : "outline"}>
                    {customer.loyalty_points > 1000 ? "VIP Customer" : "Regular Customer"}
                  </Badge>
                </div>
              </CardHeader>
              <CardContent>
                <div className="grid grid-cols-2 gap-4">
                  <div className="flex items-center space-x-2">
                    <Mail className="h-4 w-4 text-gray-400" />
                    <span className="text-sm">{customer.email || "No email provided"}</span>
                  </div>
                  <div className="flex items-center space-x-2">
                    <Phone className="h-4 w-4 text-gray-400" />
                    <span className="text-sm">{customer.phone}</span>
                  </div>
                  <div className="flex items-center space-x-2">
                    <Calendar className="h-4 w-4 text-gray-400" />
                    <span className="text-sm">Last visit: {formatDate(customer.last_visit)}</span>
                  </div>
                  <div className="flex items-center space-x-2">
                    <CreditCard className="h-4 w-4 text-gray-400" />
                    <span className="text-sm">Total spent: {formatCurrency(customer.total_spent)}</span>
                  </div>
                </div>
              </CardContent>
            </Card>

            <Card>
              <CardHeader>
                <CardTitle>Recent Transactions</CardTitle>
                <CardDescription>Latest 5 transactions from this customer</CardDescription>
              </CardHeader>
              <CardContent>
                {transactionsLoading ? (
                  <div className="flex items-center justify-center h-32">
                    <div className="animate-spin rounded-full h-6 w-6 border-b-2 border-primary"></div>
                  </div>
                ) : transactions.length > 0 ? (
                  <div className="space-y-4">
                    {transactions.map((transaction) => (
                      <div key={transaction.id} className="flex items-center justify-between p-4 border rounded-lg">
                        <div>
                          <p className="font-medium">{formatCurrency(transaction.amount)}</p>
                          <p className="text-sm text-gray-500">{formatDateTime(transaction.transaction_date)}</p>
                          {transaction.description && (
                            <p className="text-sm text-gray-600">{transaction.description}</p>
                          )}
                        </div>
                        <Badge variant={transaction.status === "completed" ? "default" : "secondary"}>
                          {transaction.status}
                        </Badge>
                      </div>
                    ))}
                  </div>
                ) : (
                  <p className="text-gray-500 text-center py-8">No transactions found</p>
                )}
              </CardContent>
            </Card>
          </div>

          <div className="space-y-6">
            <Card>
              <CardHeader>
                <CardTitle className="flex items-center space-x-2">
                  <Gift className="h-5 w-5" />
                  <span>Loyalty Status</span>
                </CardTitle>
              </CardHeader>
              <CardContent>
                <div className="space-y-4">
                  <div className="text-center">
                    <div className="text-3xl font-bold text-primary">{customer.loyalty_points}</div>
                    <p className="text-sm text-gray-600">Available Points</p>
                  </div>

                  <div className="space-y-2">
                    <div className="flex justify-between text-sm">
                      <span>Progress to next tier</span>
                      <span>{Math.min(customer.loyalty_points, 2000)}/2000</span>
                    </div>
                    <div className="w-full bg-gray-200 rounded-full h-2">
                      <div
                        className="bg-primary h-2 rounded-full"
                        style={{ width: `${Math.min((customer.loyalty_points / 2000) * 100, 100)}%` }}
                      ></div>
                    </div>
                  </div>

                  <div className="pt-4 border-t">
                    <h4 className="font-medium mb-2">Benefits</h4>
                    <ul className="text-sm text-gray-600 space-y-1">
                      <li>• Earn 1 point per KES spent</li>
                      <li>• Redeem points for discounts</li>
                      {customer.loyalty_points > 1000 && <li>• VIP customer perks</li>}
                    </ul>
                  </div>
                </div>
              </CardContent>
            </Card>

            <Card>
              <CardHeader>
                <CardTitle>Quick Actions</CardTitle>
              </CardHeader>
              <CardContent>
                <div className="space-y-2">
                  <Button variant="outline" className="w-full justify-start bg-transparent">
                    Send SMS Campaign
                  </Button>
                  <Button variant="outline" className="w-full justify-start bg-transparent">
                    View AI Insights
                  </Button>
                  <Button variant="outline" className="w-full justify-start bg-transparent">
                    Update Information
                  </Button>
                </div>
              </CardContent>
            </Card>
          </div>
        </div>
      </div>
    </DashboardLayout>
  )
}
