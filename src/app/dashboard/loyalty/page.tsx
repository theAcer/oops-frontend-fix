"use client"
import { DashboardLayout } from "@/components/layout/dashboard-layout"
import { CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card"
import { Button } from "@/components/ui/button"
import { Badge } from "@/components/ui/badge"
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from "@/components/ui/table"
import { formatDate } from "@/lib/utils"
import { Plus, Play, Settings, Users } from "lucide-react"
import Link from "next/link"
import { useLoyaltyPrograms } from "@/hooks/use-api"
import { apiService } from "@/services/api-service"
import { useAuth } from "@/contexts/auth-context"
import { BlurredCard } from "@/components/blurred-card"

export default function LoyaltyPage() {
  const { user } = useAuth()
  const merchantId = user?.merchant_id

  const { data, error, isLoading, mutate } = useLoyaltyPrograms()

  const programs = data?.programs || []

  const handleActivateProgram = async (programId: string) => {
    try {
      await apiService.activateLoyaltyProgram(programId)
      mutate() // Refresh the data
    } catch (error) {
      console.error("Failed to activate program:", error)
    }
  }

  if (error) {
    return (
      <DashboardLayout>
        <div className="flex items-center justify-center h-64">
          <p className="text-destructive">Error loading loyalty programs. Please try again.</p>
        </div>
      </DashboardLayout>
    )
  }

  return (
    <DashboardLayout>
      <div className="space-y-8">
        <div className="flex items-center justify-between">
          <div>
            <h1 className="text-3xl font-bold text-foreground">Loyalty Programs</h1>
            <p className="text-muted-foreground mt-1">Manage customer loyalty and reward programs</p>
          </div>
          <Link href="/dashboard/loyalty/create">
            <Button>
              <Plus className="h-4 w-4 mr-2" />
              Create Program
            </Button>
          </Link>
        </div>

        {/* Program Stats */}
        <div className="grid grid-cols-1 md:grid-cols-4 gap-6">
          <BlurredCard>
            <CardHeader className="pb-2">
              <CardTitle className="text-sm font-medium text-muted-foreground">Total Programs</CardTitle>
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold text-foreground">{programs.length}</div>
            </CardContent>
          </BlurredCard>

          <BlurredCard>
            <CardHeader className="pb-2">
              <CardTitle className="text-sm font-medium text-muted-foreground">Active Programs</CardTitle>
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold text-success">{programs.filter((p) => p.is_active).length}</div>
            </CardContent>
          </BlurredCard>

          <BlurredCard>
            <CardHeader className="pb-2">
              <CardTitle className="text-sm font-medium text-muted-foreground">Enrolled Customers</CardTitle>
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold text-primary">1,234</div> {/* Placeholder */}
            </CardContent>
          </BlurredCard>

          <BlurredCard>
            <CardHeader className="pb-2">
              <CardTitle className="text-sm font-medium text-muted-foreground">Points Redeemed</CardTitle>
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold text-brand-secondary">45,678</div> {/* Placeholder */}
            </CardContent>
          </BlurredCard>
        </div>

        {/* Programs Table */}
        <BlurredCard>
          <CardHeader>
            <CardTitle className="text-foreground">Loyalty Programs</CardTitle>
            <CardDescription className="text-muted-foreground">Manage your customer loyalty and reward programs</CardDescription>
          </CardHeader>
          <CardContent>
            {isLoading ? (
              <div className="flex items-center justify-center h-32">
                <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-primary"></div>
              </div>
            ) : programs.length > 0 ? (
              <Table>
                <TableHeader>
                  <TableRow>
                    <TableHead>Program Name</TableHead>
                    <TableHead>Points per KES</TableHead>
                    <TableHead>Minimum Spend</TableHead>
                    <TableHead>Status</TableHead>
                    <TableHead>Created</TableHead>
                    <TableHead>Actions</TableHead>
                  </TableRow>
                </TableHeader>
                <TableBody>
                  {programs.map((program) => (
                    <TableRow key={program.id}>
                      <TableCell>
                        <div>
                          <p className="font-medium text-foreground">{program.name}</p>
                          <p className="text-sm text-muted-foreground truncate max-w-xs">{program.description}</p>
                        </div>
                      </TableCell>
                      <TableCell className="text-foreground">{program.points_per_currency}</TableCell>
                      <TableCell className="text-foreground">KES {program.minimum_spend}</TableCell>
                      <TableCell>
                        <Badge variant={program.is_active ? "default" : "secondary"}>
                          {program.is_active ? "Active" : "Inactive"}
                        </Badge>
                      </TableCell>
                      <TableCell className="text-muted-foreground">{formatDate(program.created_at)}</TableCell>
                      <TableCell>
                        <div className="flex space-x-2">
                          {!program.is_active && (
                            <Button
                              variant="outline"
                              size="sm"
                              onClick={() => handleActivateProgram(program.id)}
                              className="bg-background/50 border-border text-foreground hover:bg-accent"
                            >
                              <Play className="h-4 w-4" />
                            </Button>
                          )}
                          <Button variant="outline" size="sm" className="bg-background/50 border-border text-foreground hover:bg-accent">
                            <Settings className="h-4 w-4" />
                          </Button>
                          <Button variant="outline" size="sm" className="bg-background/50 border-border text-foreground hover:bg-accent">
                            <Users className="h-4 w-4" />
                          </Button>
                        </div>
                      </TableCell>
                    </TableRow>
                  ))}
                </TableBody>
              </Table>
            ) : (
              <div className="text-center py-8">
                <p className="text-muted-foreground mb-4">No loyalty programs created yet</p>
                <Link href="/dashboard/loyalty/create">
                  <Button>
                    <Plus className="h-4 w-4 mr-2" />
                    Create Your First Program
                  </Button>
                </Link>
              </div>
            )}
          </CardContent>
        </BlurredCard>
      </div>
    </DashboardLayout>
  )
}