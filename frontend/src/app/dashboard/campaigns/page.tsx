"use client"
import { DashboardLayout } from "@/components/layout/dashboard-layout"
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card"
import { Button } from "@/components/ui/button"
import { Badge } from "@/components/ui/badge"
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from "@/components/ui/table"
import { formatCurrency, formatDate } from "@/lib/utils"
import { Plus, Play, BarChart3, Eye } from "lucide-react"
import Link from "next/link"
import useSWR from "swr"
import { apiService } from "@/services/api-service"
import { useAuth } from "@/contexts/auth-context"

export default function CampaignsPage() {
  const { user } = useAuth()
  const merchantId = user?.merchant_id

  const { data, error, isLoading, mutate } = useSWR(
    merchantId ? `/campaigns?merchant_id=${merchantId}` : null,
    () => merchantId && apiService.getCampaigns(merchantId),
  )

  const campaigns = data?.campaigns || []

  const handleLaunchCampaign = async (campaignId: string) => {
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
          <p className="text-red-600">Error loading campaigns. Please try again.</p>
        </div>
      </DashboardLayout>
    )
  }

  return (
    <DashboardLayout>
      <div className="space-y-6">
        <div className="flex items-center justify-between">
          <div>
            <h1 className="text-3xl font-bold text-gray-900">Marketing Campaigns</h1>
            <p className="text-gray-600">Create and manage your marketing campaigns</p>
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
          <Card>
            <CardHeader className="pb-2">
              <CardTitle className="text-sm font-medium">Total Campaigns</CardTitle>
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold">{campaigns.length}</div>
            </CardContent>
          </Card>

          <Card>
            <CardHeader className="pb-2">
              <CardTitle className="text-sm font-medium">Active Campaigns</CardTitle>
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold text-green-600">
                {campaigns.filter((c) => c.status === "active").length}
              </div>
            </CardContent>
          </Card>

          <Card>
            <CardHeader className="pb-2">
              <CardTitle className="text-sm font-medium">Draft Campaigns</CardTitle>
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold text-yellow-600">
                {campaigns.filter((c) => c.status === "draft").length}
              </div>
            </CardContent>
          </Card>

          <Card>
            <CardHeader className="pb-2">
              <CardTitle className="text-sm font-medium">Total Budget</CardTitle>
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold">
                {formatCurrency(campaigns.reduce((sum, c) => sum + c.budget, 0))}
              </div>
            </CardContent>
          </Card>
        </div>

        {/* Campaigns Table */}
        <Card>
          <CardHeader>
            <CardTitle>All Campaigns</CardTitle>
            <CardDescription>Manage your marketing campaigns and track performance</CardDescription>
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
                    <TableHead>Budget</TableHead>
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
                          <p className="font-medium">{campaign.name}</p>
                          <p className="text-sm text-gray-500 truncate max-w-xs">{campaign.description}</p>
                        </div>
                      </TableCell>
                      <TableCell>
                        <Badge variant="outline">{campaign.campaign_type}</Badge>
                      </TableCell>
                      <TableCell>{campaign.target_audience}</TableCell>
                      <TableCell>{formatCurrency(campaign.budget)}</TableCell>
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
                      <TableCell>{formatDate(campaign.start_date)}</TableCell>
                      <TableCell>
                        <div className="flex space-x-2">
                          {campaign.status === "draft" && (
                            <Button
                              variant="outline"
                              size="sm"
                              onClick={() => handleLaunchCampaign(campaign.id)}
                              className="bg-transparent"
                            >
                              <Play className="h-4 w-4" />
                            </Button>
                          )}
                          <Link href={`/dashboard/campaigns/${campaign.id}`}>
                            <Button variant="outline" size="sm" className="bg-transparent">
                              <Eye className="h-4 w-4" />
                            </Button>
                          </Link>
                          <Button variant="outline" size="sm" className="bg-transparent">
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
                <p className="text-gray-500 mb-4">No campaigns created yet</p>
                <Link href="/dashboard/campaigns/create">
                  <Button>
                    <Plus className="h-4 w-4 mr-2" />
                    Create Your First Campaign
                  </Button>
                </Link>
              </div>
            )}
          </CardContent>
        </Card>
      </div>
    </DashboardLayout>
  )
}
