"use client"

import Link from "next/link"
import { usePathname } from "next/navigation"
import { cn } from "@/lib/utils"
import { BarChart3, Users, CreditCard, Gift, Megaphone, Brain, Bell, Settings, Home, Store, KeyRound } from "lucide-react"
import { useAuth } from "@/contexts/auth-context"

interface SidebarProps {
  isCollapsed: boolean;
}

const navigation = [
  { name: "Dashboard", href: "/dashboard", icon: Home },
  { name: "Analytics", href: "/dashboard/analytics", icon: BarChart3 },
  { name: "Customers", href: "/dashboard/customers", icon: Users },
  { name: "Transactions", href: "/dashboard/transactions", icon: CreditCard },
  { name: "Loyalty Programs", href: "/dashboard/loyalty", icon: Gift },
  { name: "Campaigns", href: "/dashboard/campaigns", icon: Megaphone },
  { name: "AI Insights", href: "/dashboard/ai-insights", icon: Brain },
  { name: "Notifications", href: "/dashboard/notifications", icon: Bell },
  { name: "Settings", href: "/dashboard/settings", icon: Settings },
]

export function Sidebar({ isCollapsed }: SidebarProps) {
  const pathname = usePathname()
  const { user } = useAuth()

  return (
    <div className={cn(
      "flex h-full flex-col bg-card/70 backdrop-blur-lg border-r border-gray-200 dark:border-gray-700 transition-all duration-300",
      isCollapsed ? "w-16" : "w-64"
    )}>
      <div className="flex h-16 items-center px-6 border-b border-gray-200 dark:border-gray-700">
        {!isCollapsed && <h1 className="text-xl font-bold text-gray-900 dark:text-gray-100">Zidisha</h1>}
      </div>

      <nav className="flex-1 space-y-1 px-3 py-4 overflow-y-auto">
        {navigation.map((item) => {
          const isActive = pathname === item.href
          return (
            <Link
              key={item.name}
              href={item.href}
              className={cn(
                "group flex items-center py-2 text-sm font-medium rounded-md transition-colors",
                isActive ? "bg-primary text-primary-foreground" : "text-gray-700 hover:bg-gray-100 hover:text-gray-900 dark:text-gray-300 dark:hover:bg-gray-700 dark:hover:text-gray-100",
                isCollapsed ? "justify-center px-0" : "px-3"
              )}
            >
              <item.icon
                className={cn(
                  "h-5 w-5 flex-shrink-0",
                  isCollapsed ? "mr-0" : "mr-3",
                  isActive ? "text-primary-foreground" : "text-gray-400 group-hover:text-gray-500 dark:text-gray-500 dark:group-hover:text-gray-400",
                )}
              />
              {!isCollapsed && item.name}
            </Link>
          )
        })}

        {/* Conditional link for becoming a merchant */}
        {!user?.merchant_id && (
          <Link
            href="/dashboard/become-merchant"
            className={cn(
              "group flex items-center py-2 text-sm font-medium rounded-md transition-colors",
              pathname === "/dashboard/become-merchant" ? "bg-primary text-primary-foreground" : "text-gray-700 hover:bg-gray-100 hover:text-gray-900 dark:text-gray-300 dark:hover:bg-gray-700 dark:hover:text-gray-100",
              isCollapsed ? "justify-center px-0" : "px-3"
            )}
          >
            <Store
              className={cn(
                "h-5 w-5 flex-shrink-0",
                isCollapsed ? "mr-0" : "mr-3",
                pathname === "/dashboard/become-merchant" ? "text-primary-foreground" : "text-gray-400 group-hover:text-gray-500 dark:text-gray-500 dark:group-hover:text-gray-400",
              )}
            />
            {!isCollapsed && "Become a Merchant"}
          </Link>
        )}

        {/* Daraja Integration Link (under Settings) */}
        {user?.merchant_id && (
          <Link
            href="/dashboard/settings/daraja-integration"
            className={cn(
              "group flex items-center py-2 text-sm font-medium rounded-md transition-colors",
              pathname === "/dashboard/settings/daraja-integration" ? "bg-primary text-primary-foreground" : "text-gray-700 hover:bg-gray-100 hover:text-gray-900 dark:text-gray-300 dark:hover:bg-gray-700 dark:hover:text-gray-100",
              isCollapsed ? "justify-center px-0" : "px-3"
            )}
          >
            <KeyRound
              className={cn(
                "h-5 w-5 flex-shrink-0",
                isCollapsed ? "mr-0" : "mr-3",
                pathname === "/dashboard/settings/daraja-integration" ? "text-primary-foreground" : "text-gray-400 group-hover:text-gray-500 dark:text-gray-500 dark:group-hover:text-gray-400",
              )}
            />
            {!isCollapsed && "Daraja Integration"}
          </Link>
        )}
      </nav>
    </div>
  )
}