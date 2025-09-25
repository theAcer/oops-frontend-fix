"use client"

import { DashboardLayout } from "@/components/layout/dashboard-layout"
import { CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card"
import { Button } from "@/components/ui/button"
import { User, Store, KeyRound } from "lucide-react"
import Link from "next/link"
import { BlurredCard } from "@/components/blurred-card"
import { useAuth } from "@/contexts/auth-context"

export default function SettingsPage() {
  const { user, isMerchant } = useAuth()

  return (
    <DashboardLayout>
      <div className="space-y-8">
        <div>
          <h1 className="text-3xl font-bold text-foreground">Settings</h1>
          <p className="text-muted-foreground mt-1">Manage your account and business settings</p>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
          <BlurredCard>
            <CardHeader>
              <CardTitle className="flex items-center space-x-2 text-foreground">
                <User className="h-5 w-5 text-primary" />
                <span>Account Settings</span>
              </CardTitle>
              <CardDescription className="text-muted-foreground">Manage your personal profile and preferences.</CardDescription>
            </CardHeader>
            <CardContent>
              <Link href="/dashboard/settings/profile">
                <Button variant="outline" className="w-full justify-start bg-background/50 border-border text-foreground hover:bg-accent">
                  Edit Profile
                </Button>
              </Link>
              <Link href="/dashboard/settings/password">
                <Button variant="outline" className="w-full justify-start mt-2 bg-background/50 border-border text-foreground hover:bg-accent">
                  Change Password
                </Button>
              </Link>
            </CardContent>
          </BlurredCard>

          {isMerchant ? (
            <>
              <BlurredCard>
                <CardHeader>
                  <CardTitle className="flex items-center space-x-2 text-foreground">
                    <Store className="h-5 w-5 text-success" />
                    <span>Business Profile</span>
                  </CardTitle>
                  <CardDescription className="text-muted-foreground">Update your merchant information.</CardDescription>
                </CardHeader>
                <CardContent>
                  <Link href="/dashboard/settings/business">
                    <Button variant="outline" className="w-full justify-start bg-background/50 border-border text-foreground hover:bg-accent">
                      Edit Business Details
                    </Button>
                  </Link>
                  <Link href="/dashboard/settings/subscription">
                    <Button variant="outline" className="w-full justify-start mt-2 bg-background/50 border-border text-foreground hover:bg-accent">
                      Manage Subscription
                    </Button>
                  </Link>
                </CardContent>
              </BlurredCard>

              <BlurredCard>
                <CardHeader>
                  <CardTitle className="flex items-center space-x-2 text-foreground">
                    <KeyRound className="h-5 w-5 text-brand-secondary" />
                    <span>Integrations</span>
                  </CardTitle>
                  <CardDescription className="text-muted-foreground">Connect with external services like Daraja API.</CardDescription>
                </CardHeader>
                <CardContent>
                  <Link href="/dashboard/settings/daraja-integration">
                    <Button variant="outline" className="w-full justify-start bg-background/50 border-border text-foreground hover:bg-accent">
                      Daraja API Integration
                    </Button>
                  </Link>
                  <Link href="/dashboard/channels">
                    <Button variant="outline" className="w-full justify-start mt-2 bg-background/50 border-border text-foreground hover:bg-accent">
                      M-Pesa Channels
                    </Button>
                  </Link>
                </CardContent>
              </BlurredCard>
            </>
          ) : (
            <BlurredCard>
              <CardHeader>
                <CardTitle className="flex items-center space-x-2 text-foreground">
                  <Store className="h-5 w-5 text-primary" />
                  <span>Become a Merchant</span>
                </CardTitle>
                <CardDescription className="text-muted-foreground">Register your business to unlock all features.</CardDescription>
              </CardHeader>
              <CardContent>
                <Link href="/dashboard/become-merchant">
                  <Button className="w-full justify-start">Register Business</Button>
                </Link>
              </CardContent>
            </BlurredCard>
          )}
        </div>
      </div>
    </DashboardLayout>
  )
}