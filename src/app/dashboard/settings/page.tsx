"use client"

import { DashboardLayout } from "@/components/layout/dashboard-layout"
import { CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card"
import { Button } from "@/components/ui/button"
import { Settings, KeyRound, User, Store } from "lucide-react"
import Link from "next/link"
import { BlurredCard } from "@/components/blurred-card"
import { useAuth } from "@/contexts/auth-context"

export default function SettingsPage() {
  const { user } = useAuth()

  return (
    <DashboardLayout>
      <div className="space-y-6">
        <div>
          <h1 className="text-3xl font-bold text-gray-900">Settings</h1>
          <p className="text-gray-600">Manage your account and business settings</p>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
          <BlurredCard>
            <CardHeader>
              <CardTitle className="flex items-center space-x-2">
                <User className="h-5 w-5" />
                <span>Account Settings</span>
              </CardTitle>
              <CardDescription>Manage your personal profile and preferences.</CardDescription>
            </CardHeader>
            <CardContent>
              <Button variant="outline" className="w-full justify-start bg-transparent">
                Edit Profile
              </Button>
              <Button variant="outline" className="w-full justify-start mt-2 bg-transparent">
                Change Password
              </Button>
            </CardContent>
          </BlurredCard>

          {user?.merchant_id ? (
            <>
              <BlurredCard>
                <CardHeader>
                  <CardTitle className="flex items-center space-x-2">
                    <Store className="h-5 w-5" />
                    <span>Business Profile</span>
                  </CardTitle>
                  <CardDescription>Update your merchant information.</CardDescription>
                </CardHeader>
                <CardContent>
                  <Button variant="outline" className="w-full justify-start bg-transparent">
                    Edit Business Details
                  </Button>
                  <Button variant="outline" className="w-full justify-start mt-2 bg-transparent">
                    Manage Subscription
                  </Button>
                </CardContent>
              </BlurredCard>

              <BlurredCard>
                <CardHeader>
                  <CardTitle className="flex items-center space-x-2">
                    <KeyRound className="h-5 w-5" />
                    <span>Integrations</span>
                  </CardTitle>
                  <CardDescription>Connect with external services like Daraja API.</CardDescription>
                </CardHeader>
                <CardContent>
                  <Link href="/dashboard/settings/daraja-integration">
                    <Button variant="outline" className="w-full justify-start bg-transparent">
                      Daraja API Integration
                    </Button>
                  </Link>
                  {/* Add other integrations here */}
                </CardContent>
              </BlurredCard>
            </>
          ) : (
            <BlurredCard>
              <CardHeader>
                <CardTitle className="flex items-center space-x-2">
                  <Store className="h-5 w-5" />
                  <span>Become a Merchant</span>
                </CardTitle>
                <CardDescription>Register your business to unlock all features.</CardDescription>
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