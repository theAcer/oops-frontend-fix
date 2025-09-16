"use client"
import { DashboardLayout } from "@/components/layout/dashboard-layout"
import { CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card"
import { Button } from "@/components/ui/button"
import { Badge } from "@/components/ui/badge"
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from "@/components/ui/table"
import { formatCurrency, formatDate } from "@/lib/utils"
import { Plus, Play, BarChart3, Eye } from "lucide-react"
import Link from "next/link"
import { useCampaigns } from "@/hooks/use-api"
import { apiService } from "@/services/api-service"
import { useAuth } from "@/contexts/auth-context"
import { BlurredCard } from "@/components/blurred-card"

export default function CampaignsPage() {
  const { user } = useAuth()
  const _merchantId = user?.merchant_id // Renamed to _merchantId to ignore unused var warning

  const { data, error, isLoading, mutate } = useCampaigns()

  const campaigns = data?.campaigns || []

  const handleLaunchCampaign = async (campaignId: number) => {
    try {
      await apiService.launchCampaign(campaignId)
      mutate() // Refresh the data
    } catch (error) {
      console.error("Failed to launch campaign:", error)
    }
  }

  if (error) {
    return (
      <DashboardLayout>
        <div className="flex items-center justify-center h-64">
          <p className="text-destructive">Error loading campaigns. Please try again.</p>
        </div>
      </DashboardLayout>
    )
  }

  return (
    <DashboardLayout>
      <div className="space-y-8">
        <div className="flex items-center justify-between">
          <div>
            <h1 className="text-3xl font-bold text-foreground">Marketing Campaigns</h1>
            <p className="text-muted-foreground mt-1">Create and manage your marketing campaigns</p>
          </div>
          <Link href="/dashboard/campaigns/create">
            <Button>
              <Plus className="h-4 w-4 mr-2" />
              Create Campaign
            </Button>
          </Link>
        </div>

        {/* Campaign Stats */}
        <div className="grid grid-cols-1 md:grid-cols-4 gap-6">
          <BlurredCard>
            <CardHeader className="pb-2">
              <CardTitle className="text-sm font-medium text-muted-foreground">Total Campaigns</CardTitle>
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold text-foreground">{campaigns.length}</div>
            </CardContent>
          </BlurredCard>

          <BlurredCard>
            <CardHeader className="pb-2">
              <CardTitle className="text-sm font-medium text-muted-foreground">Active Campaigns</CardTitle>
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold text-success">
                {campaigns.filter((c) => c.status === "active").length}
              </div>
            </CardContent>
          </BlurredCard>

          <BlurredCard>
            <CardHeader className="pb-2">
              <CardTitle className="text-sm font-medium text-muted-foreground">Draft Campaigns</CardTitle>
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold text-warning">
                {campaigns.filter((c) => c.status === "draft").length}
              </div>
            </CardContent>
          </BlurredCard>

          <BlurredCard>
            <CardHeader className="pb-2">
              <CardTitle className="text-sm font-medium text-muted-foreground">Total Budget</CardTitle>
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold text-primary">
                {formatCurrency(campaigns.reduce((sum, c) => sum + c.minimum_spend, 0))} {/* Assuming budget is minimum_spend for now */}
              </div>
            </CardContent>
          </BlurredCard>
        </div>

        {/* Campaigns Table */}
        <BlurredCard>
          <CardHeader>
            <CardTitle className="text-foreground">All Campaigns</CardTitle>
            <CardDescription className="text-muted-foreground">Manage your marketing campaigns and track performance</CardDescription>
          </CardHeader>
          <CardContent>
            {isLoading ? (
              <div className="flex items-center justify-center h-32">
                <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-primary"></div>
              </div>
            ) : campaigns.length > 0 ? (
              <Table>
                <TableHeader>
                  <TableRow>
                    <TableHead>Campaign Name</TableHead>
                    <TableHead>Type</TableHead>
                    <TableHead>Target Audience</TableHead>
                    <TableHead>Min. Spend</TableHead>
                    <TableHead>Status</TableHead>
                    <TableHead>Start Date</TableHead>
                    <TableHead>Actions</TableHead>
                  </TableRow>
                </TableHeader>
                <TableBody>
                  {campaigns.map((campaign) => (
                    <TableRow key={campaign.id}>
                      <TableCell>
                        <div>
                          <p className="font-medium text-foreground">{campaign.name}</p>
                          <p className="text-sm text-muted-foreground truncate max-w-xs">{campaign.description}</p>
                        </div>
                      </TableCell>
                      <TableCell>
                        <Badge variant="outline" className="bg-secondary/50 text-secondary-foreground">{campaign.campaign_type}</Badge>
                      </TableCell>
                      <TableCell className="text-muted-foreground">{campaign.target_audience}</TableCell>
                      <TableCell className="text-foreground">{formatCurrency(campaign.minimum_spend)}</TableCell>
                      <TableCell>
                        <Badge
                          variant={
                            campaign.status === "active"
                              ? "default"
                              : campaign.status === "draft"
                                ? "secondary"
                                : "outline"
                          }
                        >
                          {campaign.status}
                        </Badge>
                      </TableCell>
                      <TableCell className="text-muted-foreground">{formatDate(campaign.created_at)}</TableCell> {/* Using created_at as start_date is optional */}
                      <TableCell>
                        <div className="flex space-x-2">
                          {campaign.status === "draft" && (
                            <Button
                              variant="outline"
                              size="sm"
                              onClick={() => handleLaunchCampaign(campaign.id)}
                              className="bg-background/50 border-border text-foreground hover:bg-accent"
                            >
                              <Play className="h-4 w-4" />
                            </Button>
                          )}
                          <Link href={`/dashboard/campaigns/${campaign.id}`}>
                            <Button variant="outline" size="sm" className="bg-background/50 border-border text-foreground hover:bg-accent">
                              <Eye className="h-4 w-4" />
                            </Button>
                          </Link>
                          <Button variant="outline" size="sm" className="bg-background/50 border-border text-foreground hover:bg-accent">
                            <BarChart3 className="h-4 w-4" />
                          </Button>
                        </div>
                      </TableCell>
                    </TableRow>
                  ))}
                </TableBody>
              </Table>
            ) : (
              <div className="text-center py-8">
                <p className="text-muted-foreground mb-4">No campaigns created yet</p>
                <Link href="/dashboard/campaigns/create">
                  <Button>
                    <Plus className="h-4 w-4 mr-2" />
                    Create Your First Campaign
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