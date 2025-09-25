"use client"

import { DashboardLayout } from "@/components/layout/dashboard-layout"
import { CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card"
import { Button } from "@/components/ui/button"
import { Badge } from "@/components/ui/badge"
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from "@/components/ui/table"
import { DropdownMenu, DropdownMenuContent, DropdownMenuItem, DropdownMenuTrigger } from "@/components/ui/dropdown-menu"
import Link from "next/link"
import { BlurredCard } from "@/components/blurred-card"
import { apiService } from "@/services/api-service"

// Mock data - will be replaced with real API calls
const mockChannels = [
  {
    id: 1,
    name: "Main PayBill",
    type: "PayBill",
    shortcode: "174379",
    environment: "sandbox",
    status: "verified",
    urls_registered: true,
    receiving: false,
    created_at: "2024-01-15T10:30:00Z"
  },
  {
    id: 2,
    name: "Test Channel",
    type: "PayBill",
    shortcode: "174378",
    environment: "sandbox",
    status: "unverified",
    urls_registered: false,
    receiving: false,
    created_at: "2024-01-16T14:20:00Z"
  }
]

const getStatusBadge = (status: string) => {
  switch (status) {
    case "verified":
      return <Badge variant="default" className="bg-green-100 text-green-800 border-green-200"><CheckCircle className="w-3 h-3 mr-1" />Verified</Badge>
    case "unverified":
      return <Badge variant="secondary"><XCircle className="w-3 h-3 mr-1" />Unverified</Badge>
    case "urls_registered":
      return <Badge variant="default" className="bg-blue-100 text-blue-800 border-blue-200"><Clock className="w-3 h-3 mr-1" />URLs Registered</Badge>
    case "receiving":
      return <Badge variant="default" className="bg-purple-100 text-purple-800 border-purple-200"><Radio className="w-3 h-3 mr-1" />Receiving</Badge>
    default:
      return <Badge variant="outline">{status}</Badge>
  }
}

const getEnvironmentBadge = (environment: string) => {
  return environment === "sandbox"
    ? <Badge variant="outline" className="bg-yellow-50 text-yellow-700 border-yellow-200">Sandbox</Badge>
    : <Badge variant="outline" className="bg-blue-50 text-blue-700 border-blue-200">Production</Badge>
}

export default function ChannelsPage() {
  const [channels, setChannels] = useState(mockChannels)

  const handleVerify = async (channelId: number) => {
    try {
      // TODO: Replace with actual API call
      // await apiService.verifyMpesaChannel(channelId)
      toast.success("Channel verification started")
      // Update channel status in UI
      setChannels(prev => prev.map(ch =>
        ch.id === channelId ? { ...ch, status: "verified" } : ch
      ))
    } catch (error) {
      toast.error("Failed to verify channel")
    }
  }

  const handleRegisterUrls = async (channelId: number) => {
    try {
      // TODO: Replace with actual API call
      // await apiService.registerMpesaUrls(channelId)
      toast.success("URL registration started")
      // Update channel status in UI
      setChannels(prev => prev.map(ch =>
        ch.id === channelId ? { ...ch, status: "urls_registered" } : ch
      ))
    } catch (error) {
      toast.error("Failed to register URLs")
    }
  }

  const handleSimulate = async (channelId: number) => {
    try {
      // TODO: Replace with actual API call
      // await apiService.simulateMpesaTransaction(channelId, simulationData)
      toast.success("Payment simulation completed")
    } catch (error) {
      toast.error("Failed to simulate payment")
    }
  }
  return (
    <DashboardLayout>
      <div className="space-y-8">
        <div className="flex items-center justify-between">
          <div className="flex items-center space-x-4">
            <Link href="/dashboard">
              <Button variant="ghost" size="sm" className="text-muted-foreground hover:bg-accent hover:text-foreground">
                <ArrowLeft className="h-4 w-4 mr-2" />
                Back to Dashboard
              </Button>
            </Link>
            <div>
              <h1 className="text-3xl font-bold text-foreground">M-Pesa Channels</h1>
              <p className="text-muted-foreground mt-1">Manage your M-Pesa integration channels</p>
            </div>
          </div>
          <Link href="/dashboard/channels/add">
            <Button className="bg-primary hover:bg-primary/90">
              <Plus className="h-4 w-4 mr-2" />
              Add Channel
            </Button>
          </Link>
        </div>

        <BlurredCard>
          <CardHeader>
            <CardTitle className="text-foreground">Your Channels</CardTitle>
            <CardDescription className="text-muted-foreground">
              Manage your M-Pesa channels for payment processing and transaction tracking
            </CardDescription>
          </CardHeader>
          <CardContent>
            {mockChannels.length === 0 ? (
              <div className="text-center py-8">
                <p className="text-muted-foreground mb-4">No M-Pesa channels configured yet</p>
                <Link href="/dashboard/channels/add">
                  <Button>Add Your First Channel</Button>
                </Link>
              </div>
            ) : (
              <Table>
                <TableHeader>
                  <TableRow>
                    <TableHead>Name</TableHead>
                    <TableHead>Type</TableHead>
                    <TableHead>Shortcode</TableHead>
                    <TableHead>Environment</TableHead>
                    <TableHead>Status</TableHead>
                    <TableHead>Created</TableHead>
                    <TableHead className="w-[50px]"></TableHead>
                  </TableRow>
                </TableHeader>
                <TableBody>
                  {mockChannels.map((channel) => (
                    <TableRow key={channel.id}>
                      <TableCell className="font-medium">{channel.name}</TableCell>
                      <TableCell>{channel.type}</TableCell>
                      <TableCell className="font-mono">{channel.shortcode}</TableCell>
                      <TableCell>{getEnvironmentBadge(channel.environment)}</TableCell>
                      <TableCell>{getStatusBadge(channel.status)}</TableCell>
                      <TableCell className="text-muted-foreground">
                        {new Date(channel.created_at).toLocaleDateString()}
                      </TableCell>
                      <TableCell>
                        <DropdownMenu>
                          <DropdownMenuTrigger asChild>
                            <Button variant="ghost" size="sm">
                              <MoreHorizontal className="h-4 w-4" />
                            </Button>
                          </DropdownMenuTrigger>
                          <DropdownMenuContent align="end">
                            <DropdownMenuItem onClick={() => handleVerify(channel.id)}>
                              Verify Channel
                            </DropdownMenuItem>
                            <DropdownMenuItem onClick={() => handleRegisterUrls(channel.id)}>
                              Register URLs
                            </DropdownMenuItem>
                            <DropdownMenuItem onClick={() => handleSimulate(channel.id)}>
                              Simulate Payment
                            </DropdownMenuItem>
                            <DropdownMenuItem onClick={() => window.open(`/dashboard/channels/analytics`, '_blank')}>
                              View Analytics
                            </DropdownMenuItem>
                          </DropdownMenuContent>
                        </DropdownMenu>
                      </TableCell>
                    </TableRow>
                  ))}
                </TableBody>
              </Table>
            )}
          </CardContent>
        </BlurredCard>
      </div>
    </DashboardLayout>
  )
}
