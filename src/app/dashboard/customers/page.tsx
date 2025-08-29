"use client"

import { useState } from "react"
import { DashboardLayout } from "@/components/layout/dashboard-layout"
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card"
import { Button } from "@/components/ui/button"
import { Input } from "@/components/ui/input"
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from "@/components/ui/table"
import { Badge } from "@/components/ui/badge"
import { useCustomers } from "@/hooks/use-api"
import { formatCurrency, formatDate } from "@/lib/utils"
import { Search, Plus, Eye } from "lucide-react"
import Link from "next/link"

export default function CustomersPage() {
  const [page, setPage] = useState(1)
  const [searchTerm, setSearchTerm] = useState("")
  const { data, error, isLoading } = useCustomers(page, 10)

  const customers = data?.customers || []
  const total = data?.total || 0

  if (error) {
    return (
      <DashboardLayout>
        <div className="flex items-center justify-center h-64">
          <p className="text-red-600">Error loading customers. Please try again.</p>
        </div>
      </DashboardLayout>
    )
  }

  return (
    <DashboardLayout>
      <div className="space-y-6">
        <div className="flex items-center justify-between">
          <div>
            <h1 className="text-3xl font-bold text-gray-900">Customers</h1>
            <p className="text-gray-600">Manage your customer relationships and loyalty</p>
          </div>
          <Button>
            <Plus className="h-4 w-4 mr-2" />
            Add Customer
          </Button>
        </div>

        <Card>
          <CardHeader>
            <CardTitle>Customer List</CardTitle>
            <CardDescription>All your customers and their loyalty status</CardDescription>
          </CardHeader>
          <CardContent>
            <div className="flex items-center space-x-4 mb-6">
              <div className="relative flex-1 max-w-sm">
                <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 text-gray-400 h-4 w-4" />
                <Input
                  placeholder="Search customers..."
                  value={searchTerm}
                  onChange={(e) => setSearchTerm(e.target.value)}
                  className="pl-10"
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
                    <TableHead>Name</TableHead>
                    <TableHead>Contact</TableHead>
                    <TableHead>Total Spent</TableHead>
                    <TableHead>Loyalty Points</TableHead>
                    <TableHead>Last Visit</TableHead>
                    <TableHead>Status</TableHead>
                    <TableHead>Actions</TableHead>
                  </TableRow>
                </TableHeader>
                <TableBody>
                  {customers.map((customer) => (
                    <TableRow key={customer.id}>
                      <TableCell className="font-medium">{customer.name}</TableCell>
                      <TableCell>
                        <div className="space-y-1">
                          {customer.email && <div className="text-sm">{customer.email}</div>}
                          <div className="text-sm text-gray-500">{customer.phone}</div>
                        </div>
                      </TableCell>
                      <TableCell>{formatCurrency(customer.total_spent)}</TableCell>
                      <TableCell>
                        <Badge variant="secondary">{customer.loyalty_points} pts</Badge>
                      </TableCell>
                      <TableCell>{formatDate(customer.last_visit)}</TableCell>
                      <TableCell>
                        <Badge variant={customer.loyalty_points > 1000 ? "default" : "outline"}>
                          {customer.loyalty_points > 1000 ? "VIP" : "Regular"}
                        </Badge>
                      </TableCell>
                      <TableCell>
                        <Link href={`/dashboard/customers/${customer.id}`}>
                          <Button variant="ghost" size="sm">
                            <Eye className="h-4 w-4" />
                          </Button>
                        </Link>
                      </TableCell>
                    </TableRow>
                  ))}
                </TableBody>
              </Table>
            )}

            {customers.length === 0 && !isLoading && (
              <div className="text-center py-8">
                <p className="text-gray-500">No customers found</p>
              </div>
            )}

            {total > 10 && (
              <div className="flex items-center justify-between mt-6">
                <p className="text-sm text-gray-600">
                  Showing {(page - 1) * 10 + 1} to {Math.min(page * 10, total)} of {total} customers
                </p>
                <div className="flex space-x-2">
                  <Button variant="outline" size="sm" disabled={page === 1} onClick={() => setPage(page - 1)}>
                    Previous
                  </Button>
                  <Button variant="outline" size="sm" disabled={page * 10 >= total} onClick={() => setPage(page + 1)}>
                    Next
                  </Button>
                </div>
              </div>
            )}
          </CardContent>
        </Card>
      </div>
    </DashboardLayout>
  )
}
