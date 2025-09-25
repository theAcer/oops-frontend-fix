"use client"

import React, { useState } from "react"
import { useOnboarding } from "@/contexts/onboarding-context"
import { useAuth } from "@/contexts/auth-context"
import { Button } from "@/components/ui/button"
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card"
import { Badge } from "@/components/ui/badge"
import { Separator } from "@/components/ui/separator"
import { Progress } from "@/components/ui/progress"
import { Alert, AlertDescription } from "@/components/ui/alert"
import { 
  Rocket, 
  CheckCircle, 
  Building, 
  CreditCard, 
  Gift, 
  Users,
  TrendingUp,
  Shield,
  AlertTriangle,
  Loader2,
  ExternalLink,
  Copy,
  Eye
} from "lucide-react"
import { toast } from "react-hot-toast"

interface LaunchStepProps {
  onComplete: () => void
}

export function LaunchStep({ onComplete }: LaunchStepProps) {
  const { data, validateBusinessInfo, validateMpesaChannels, validateLoyaltyProgram } = useOnboarding()
  const { user } = useAuth()
  const [isLaunching, setIsLaunching] = useState(false)
  const [launchProgress, setLaunchProgress] = useState(0)
  const [currentTask, setCurrentTask] = useState("")
  const [launchResults, setLaunchResults] = useState<any>(null)

  const validationChecks = [
    {
      id: "business",
      title: "Business Information",
      description: "Complete business details",
      icon: Building,
      validate: validateBusinessInfo,
      status: validateBusinessInfo() ? "complete" : "incomplete"
    },
    {
      id: "mpesa",
      title: "M-Pesa Channels",
      description: "At least one M-Pesa channel configured",
      icon: CreditCard,
      validate: validateMpesaChannels,
      status: validateMpesaChannels() ? "complete" : "incomplete"
    },
    {
      id: "loyalty",
      title: "Loyalty Program",
      description: "Loyalty program configuration",
      icon: Gift,
      validate: validateLoyaltyProgram,
      status: validateLoyaltyProgram() ? "complete" : "incomplete"
    }
  ]

  const allValidationsPassed = validationChecks.every(check => check.status === "complete")

  const handleLaunch = async () => {
    if (!allValidationsPassed) {
      toast.error("Please complete all required steps before launching")
      return
    }

    setIsLaunching(true)
    setLaunchProgress(0)

    try {
      // Step 1: Create merchant
      setCurrentTask("Creating merchant account...")
      setLaunchProgress(20)
      
      // Simulate API call delay
      await new Promise(resolve => setTimeout(resolve, 1500))
      
      const merchantResponse = await createMerchant()
      
      // Step 2: Create M-Pesa channels
      setCurrentTask("Setting up M-Pesa channels...")
      setLaunchProgress(40)
      
      await new Promise(resolve => setTimeout(resolve, 1000))
      
      const channelResults = await createMpesaChannels(merchantResponse.id)
      
      // Step 3: Create loyalty program
      setCurrentTask("Configuring loyalty program...")
      setLaunchProgress(60)
      
      await new Promise(resolve => setTimeout(resolve, 1000))
      
      const loyaltyResponse = await createLoyaltyProgram(merchantResponse.id)
      
      // Step 4: Verify integrations
      setCurrentTask("Verifying integrations...")
      setLaunchProgress(80)
      
      await new Promise(resolve => setTimeout(resolve, 1000))
      
      const verificationResults = await verifyIntegrations(channelResults)
      
      // Step 5: Complete setup
      setCurrentTask("Finalizing setup...")
      setLaunchProgress(100)
      
      await new Promise(resolve => setTimeout(resolve, 500))
      
      setLaunchResults({
        merchant: merchantResponse,
        channels: channelResults,
        loyalty: loyaltyResponse,
        verification: verificationResults
      })
      
      toast.success("Platform launched successfully!")
      
      // Complete onboarding after a short delay
      setTimeout(() => {
        onComplete()
      }, 2000)
      
    } catch (error) {
      console.error("Launch error:", error)
      toast.error("Launch failed. Please try again.")
      setIsLaunching(false)
      setLaunchProgress(0)
      setCurrentTask("")
    }
  }

  const createMerchant = async () => {
    // Mock API call - replace with actual API integration
    return {
      id: Math.floor(Math.random() * 1000),
      business_name: data.businessInfo.businessName,
      owner_name: data.businessInfo.ownerName,
      email: data.businessInfo.email,
      phone: data.businessInfo.phone,
      business_type: data.businessInfo.businessType,
      status: "active"
    }
  }

  const createMpesaChannels = async (merchantId: number) => {
    // Mock API calls for each channel
    const results = []
    
    for (const channel of data.mpesaChannels) {
      const result = {
        id: Math.floor(Math.random() * 1000),
        merchant_id: merchantId,
        name: channel.name,
        shortcode: channel.shortcode,
        channel_type: channel.channel_type,
        environment: channel.environment,
        status: "configured",
        is_primary: channel.is_primary
      }
      results.push(result)
    }
    
    return results
  }

  const createLoyaltyProgram = async (merchantId: number) => {
    // Mock API call
    return {
      id: Math.floor(Math.random() * 1000),
      merchant_id: merchantId,
      name: data.loyaltyProgram.name,
      description: data.loyaltyProgram.description,
      points_per_shilling: data.loyaltyProgram.points_per_shilling,
      redemption_rate: data.loyaltyProgram.redemption_rate,
      tier_system_enabled: data.loyaltyProgram.tier_system_enabled,
      tiers: data.loyaltyProgram.tiers,
      status: "active"
    }
  }

  const verifyIntegrations = async (channels: any[]) => {
    // Mock verification results
    return channels.map(channel => ({
      channel_id: channel.id,
      verified: channel.environment === "sandbox", // Sandbox always verifies
      status: channel.environment === "sandbox" ? "verified" : "pending_verification"
    }))
  }

  const copyToClipboard = (text: string) => {
    navigator.clipboard.writeText(text)
    toast.success("Copied to clipboard")
  }

  if (launchResults) {
    return (
      <div className="space-y-6">
        <div className="text-center">
          <div className="w-16 h-16 bg-green-100 dark:bg-green-900/20 rounded-full flex items-center justify-center mx-auto mb-4">
            <CheckCircle className="h-8 w-8 text-green-600 dark:text-green-400" />
          </div>
          <h3 className="text-2xl font-bold text-foreground mb-2">
            🎉 Platform Launched Successfully!
          </h3>
          <p className="text-muted-foreground">
            Your loyalty platform is now live and ready to accept customers
          </p>
        </div>

        {/* Launch Summary */}
        <Card>
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              <Rocket className="h-5 w-5" />
              Launch Summary
            </CardTitle>
          </CardHeader>
          <CardContent className="space-y-4">
            <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
              <div className="text-center p-4 bg-muted/50 rounded-lg">
                <Building className="h-6 w-6 mx-auto mb-2 text-primary" />
                <div className="font-medium">Merchant Created</div>
                <div className="text-sm text-muted-foreground">ID: {launchResults.merchant.id}</div>
              </div>
              <div className="text-center p-4 bg-muted/50 rounded-lg">
                <CreditCard className="h-6 w-6 mx-auto mb-2 text-primary" />
                <div className="font-medium">{launchResults.channels.length} Channels</div>
                <div className="text-sm text-muted-foreground">M-Pesa Integration</div>
              </div>
              <div className="text-center p-4 bg-muted/50 rounded-lg">
                <Gift className="h-6 w-6 mx-auto mb-2 text-primary" />
                <div className="font-medium">Loyalty Program</div>
                <div className="text-sm text-muted-foreground">Active & Ready</div>
              </div>
            </div>

            <Separator />

            {/* Channel Status */}
            <div>
              <h4 className="font-medium mb-3">M-Pesa Channel Status</h4>
              <div className="space-y-2">
                {launchResults.channels.map((channel: any, index: number) => {
                  const verification = launchResults.verification.find((v: any) => v.channel_id === channel.id)
                  return (
                    <div key={channel.id} className="flex items-center justify-between p-3 bg-muted/30 rounded-lg">
                      <div className="flex items-center gap-3">
                        <CreditCard className="h-4 w-4" />
                        <div>
                          <div className="font-medium">{channel.name}</div>
                          <div className="text-sm text-muted-foreground">
                            {channel.channel_type.toUpperCase()} • {channel.shortcode}
                          </div>
                        </div>
                      </div>
                      <div className="flex items-center gap-2">
                        {channel.is_primary && (
                          <Badge variant="default" className="text-xs">Primary</Badge>
                        )}
                        <Badge 
                          variant={verification?.verified ? "default" : "secondary"}
                          className={verification?.verified ? "bg-green-600" : ""}
                        >
                          {verification?.status || "configured"}
                        </Badge>
                      </div>
                    </div>
                  )
                })}
              </div>
            </div>
          </CardContent>
        </Card>

        {/* Next Steps */}
        <Card>
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              <TrendingUp className="h-5 w-5" />
              Next Steps
            </CardTitle>
            <CardDescription>
              Recommended actions to get the most out of your platform
            </CardDescription>
          </CardHeader>
          <CardContent>
            <div className="space-y-3">
              <div className="flex items-center gap-3 p-3 bg-blue-50 dark:bg-blue-950/20 rounded-lg">
                <Users className="h-5 w-5 text-blue-600" />
                <div>
                  <div className="font-medium">Invite Your Team</div>
                  <div className="text-sm text-muted-foreground">Add team members to help manage your loyalty program</div>
                </div>
              </div>
              <div className="flex items-center gap-3 p-3 bg-green-50 dark:bg-green-950/20 rounded-lg">
                <Shield className="h-5 w-5 text-green-600" />
                <div>
                  <div className="font-medium">Test Your Integration</div>
                  <div className="text-sm text-muted-foreground">Run test transactions to ensure everything works correctly</div>
                </div>
              </div>
              <div className="flex items-center gap-3 p-3 bg-purple-50 dark:bg-purple-950/20 rounded-lg">
                <Gift className="h-5 w-5 text-purple-600" />
                <div>
                  <div className="font-medium">Launch Marketing Campaign</div>
                  <div className="text-sm text-muted-foreground">Promote your new loyalty program to existing customers</div>
                </div>
              </div>
            </div>
          </CardContent>
        </Card>

        <div className="text-center">
          <Button onClick={onComplete} size="lg" className="px-8">
            Go to Dashboard
          </Button>
        </div>
      </div>
    )
  }

  return (
    <div className="space-y-6">
      <div className="text-center mb-6">
        <h3 className="text-xl font-semibold text-foreground mb-2">
          Ready to Launch Your Platform?
        </h3>
        <p className="text-muted-foreground">
          Review your configuration and launch your loyalty platform
        </p>
      </div>

      {/* Pre-launch Validation */}
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <CheckCircle className="h-5 w-5" />
            Pre-launch Checklist
          </CardTitle>
          <CardDescription>
            Ensure all requirements are met before launching
          </CardDescription>
        </CardHeader>
        <CardContent>
          <div className="space-y-3">
            {validationChecks.map((check) => {
              const Icon = check.icon
              const isComplete = check.status === "complete"
              
              return (
                <div
                  key={check.id}
                  className={`flex items-center gap-3 p-3 rounded-lg border ${
                    isComplete 
                      ? "border-green-200 bg-green-50 dark:border-green-800 dark:bg-green-950/20" 
                      : "border-red-200 bg-red-50 dark:border-red-800 dark:bg-red-950/20"
                  }`}
                >
                  <div className={`p-2 rounded-full ${
                    isComplete ? "bg-green-100 dark:bg-green-900/40" : "bg-red-100 dark:bg-red-900/40"
                  }`}>
                    {isComplete ? (
                      <CheckCircle className="h-4 w-4 text-green-600 dark:text-green-400" />
                    ) : (
                      <AlertTriangle className="h-4 w-4 text-red-600 dark:text-red-400" />
                    )}
                  </div>
                  <Icon className={`h-5 w-5 ${
                    isComplete ? "text-green-600 dark:text-green-400" : "text-red-600 dark:text-red-400"
                  }`} />
                  <div className="flex-1">
                    <div className="font-medium">{check.title}</div>
                    <div className="text-sm text-muted-foreground">{check.description}</div>
                  </div>
                  <Badge 
                    variant={isComplete ? "default" : "destructive"}
                    className={isComplete ? "bg-green-600" : ""}
                  >
                    {isComplete ? "Complete" : "Incomplete"}
                  </Badge>
                </div>
              )
            })}
          </div>
        </CardContent>
      </Card>

      {/* Configuration Summary */}
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <Eye className="h-5 w-5" />
            Configuration Summary
          </CardTitle>
          <CardDescription>
            Review your platform configuration
          </CardDescription>
        </CardHeader>
        <CardContent className="space-y-4">
          {/* Business Info */}
          <div>
            <h4 className="font-medium mb-2 flex items-center gap-2">
              <Building className="h-4 w-4" />
              Business Information
            </h4>
            <div className="grid grid-cols-1 md:grid-cols-2 gap-3 text-sm">
              <div className="flex justify-between">
                <span className="text-muted-foreground">Business Name:</span>
                <span className="font-medium">{data.businessInfo.businessName}</span>
              </div>
              <div className="flex justify-between">
                <span className="text-muted-foreground">Owner:</span>
                <span className="font-medium">{data.businessInfo.ownerName}</span>
              </div>
              <div className="flex justify-between">
                <span className="text-muted-foreground">Email:</span>
                <span className="font-medium">{data.businessInfo.email}</span>
              </div>
              <div className="flex justify-between">
                <span className="text-muted-foreground">Phone:</span>
                <span className="font-medium">{data.businessInfo.phone}</span>
              </div>
            </div>
          </div>

          <Separator />

          {/* M-Pesa Channels */}
          <div>
            <h4 className="font-medium mb-2 flex items-center gap-2">
              <CreditCard className="h-4 w-4" />
              M-Pesa Channels ({data.mpesaChannels.length})
            </h4>
            <div className="space-y-2">
              {data.mpesaChannels.map((channel, index) => (
                <div key={index} className="flex items-center justify-between p-2 bg-muted/30 rounded">
                  <div className="flex items-center gap-2">
                    <span className="font-medium">{channel.name}</span>
                    <Badge variant="outline" className="text-xs">
                      {channel.channel_type.toUpperCase()}
                    </Badge>
                    {channel.is_primary && (
                      <Badge variant="default" className="text-xs">Primary</Badge>
                    )}
                  </div>
                  <div className="flex items-center gap-2">
                    <span className="text-sm text-muted-foreground">{channel.shortcode}</span>
                    <Badge 
                      variant="secondary"
                      className={channel.environment === "production" ? "bg-green-100 text-green-800" : "bg-yellow-100 text-yellow-800"}
                    >
                      {channel.environment}
                    </Badge>
                  </div>
                </div>
              ))}
            </div>
          </div>

          <Separator />

          {/* Loyalty Program */}
          <div>
            <h4 className="font-medium mb-2 flex items-center gap-2">
              <Gift className="h-4 w-4" />
              Loyalty Program
            </h4>
            <div className="grid grid-cols-1 md:grid-cols-2 gap-3 text-sm">
              <div className="flex justify-between">
                <span className="text-muted-foreground">Program Name:</span>
                <span className="font-medium">{data.loyaltyProgram.name}</span>
              </div>
              <div className="flex justify-between">
                <span className="text-muted-foreground">Points per KES:</span>
                <span className="font-medium">{data.loyaltyProgram.points_per_shilling}</span>
              </div>
              <div className="flex justify-between">
                <span className="text-muted-foreground">Redemption Rate:</span>
                <span className="font-medium">{data.loyaltyProgram.redemption_rate} pts = 1 KES</span>
              </div>
              <div className="flex justify-between">
                <span className="text-muted-foreground">Tier System:</span>
                <span className="font-medium">
                  {data.loyaltyProgram.tier_system_enabled ? `${data.loyaltyProgram.tiers?.length || 0} tiers` : "Disabled"}
                </span>
              </div>
            </div>
          </div>
        </CardContent>
      </Card>

      {/* Launch Progress */}
      {isLaunching && (
        <Card>
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              <Loader2 className="h-5 w-5 animate-spin" />
              Launching Platform...
            </CardTitle>
          </CardHeader>
          <CardContent>
            <div className="space-y-4">
              <div>
                <div className="flex justify-between text-sm mb-2">
                  <span>{currentTask}</span>
                  <span>{launchProgress}%</span>
                </div>
                <Progress value={launchProgress} className="h-2" />
              </div>
              <p className="text-sm text-muted-foreground">
                Please wait while we set up your loyalty platform. This may take a few moments.
              </p>
            </div>
          </CardContent>
        </Card>
      )}

      {/* Launch Button */}
      {!isLaunching && (
        <>
          {!allValidationsPassed && (
            <Alert>
              <AlertTriangle className="h-4 w-4" />
              <AlertDescription>
                Please complete all required steps before launching your platform.
              </AlertDescription>
            </Alert>
          )}

          <div className="text-center">
            <Button
              onClick={handleLaunch}
              disabled={!allValidationsPassed || isLaunching}
              size="lg"
              className="px-8 bg-green-600 hover:bg-green-700"
            >
              <Rocket className="h-5 w-5 mr-2" />
              Launch My Loyalty Platform
            </Button>
            <p className="text-sm text-muted-foreground mt-2">
              This will create your merchant account and set up all integrations
            </p>
          </div>
        </>
      )}
    </div>
  )
}
