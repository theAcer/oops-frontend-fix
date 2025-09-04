"use client"

import { useState } from "react"
import { DashboardLayout } from "@/components/layout/dashboard-layout"
import { CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card"
import { Button } from "@/components/ui/button"
import { Input } from "@/components/ui/input"
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from "@/components/ui/table"
import { Badge } from "@/components/ui/badge"
import { useCustomers } from "@/hooks/use-api"
import { formatCurrency, formatDate } from "@/lib/utils"
import { Search, Plus, Eye } from "lucide-react"
import Link from "next/link"
import { BlurredCard } from "@/components/blurred-card"

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
          <p className="text-destructive">Error loading customers. Please try again.</p>
        </div>
      </DashboardLayout>
    )
  }

  return (
    <DashboardLayout>
      <div className="space-y-8">
        <div className="flex items-center justify-between">
          <div>
            <h1 className="text-3xl font-bold text-foreground">Customers</h1>
            <p className="text-muted-foreground mt-1">Manage your customer relationships and loyalty</p>
          </div>
          <Button>
            <Plus className="h-4 w-4 mr-2" />
            Add Customer
          </Button>
        </div>

        <BlurredCard>
          <CardHeader>
            <CardTitle className="text-foreground">Customer List</CardTitle>
            <CardDescription className="text-muted-foreground">All your customers and their loyalty status</CardDescription>
          </CardHeader>
          <CardContent>
            <div className="flex items-center space-x-4 mb-6">
              <div className="relative flex-1 max-w-sm">
                <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 text-muted-foreground h-4 w-4" />
                <Input
                  placeholder="Search customers..."
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
                      <TableCell className="font-medium text-foreground">{customer.name}</TableCell>
                      <TableCell>
                        <div className="space-y-1">
                          {customer.email && <div className="text-sm text-muted-foreground">{customer.email}</div>}
                          <div className="text-sm text-muted-foreground">{customer.phone}</div>
                        </div>
                      </TableCell>
                      <TableCell className="text-foreground">{formatCurrency(customer.total_spent)}</TableCell>
                      <TableCell>
                        <Badge variant="secondary" className="bg-secondary/50 text-secondary-foreground">
                          {customer.loyalty_points} pts
                        </Badge>
                      </TableCell>
                      <TableCell className="text-muted-foreground">{formatDate(customer.last_visit)}</TableCell>
                      <TableCell>
                        <Badge variant={customer.loyalty_points > 1000 ? "default" : "outline"}>
                          {customer.loyalty_points > 1000 ? "VIP" : "Regular"}
                        </Badge>
                      </TableCell>
                      <TableCell>
                        <Link href={`/dashboard/customers/${customer.id}`}>
                          <Button variant="ghost" size="sm" className="text-muted-foreground hover:bg-accent hover:text-foreground">
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
                <p className="text-muted-foreground mb-4">No customers found</p>
              </div>
            )}

            {total > 10 && (
              <div className="flex items-center justify-between mt-6">
                <p className="text-sm text-muted-foreground">
                  Showing {(page - 1) * 10 + 1} to {Math.min(page * 10, total)} of {total} customers
                </p>
                <div className="flex space-x-2">
                  <Button variant="outline" size="sm" disabled={page === 1} onClick={() => setPage(page - 1)} className="bg-background/50 border-border text-foreground hover:bg-accent">
                    Previous
                  </Button>
                  <Button variant="outline" size="sm" disabled={page * 10 >= total} onClick={() => setPage(page + 1)} className="bg-background/50 border-border text-foreground hover:bg-accent">
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