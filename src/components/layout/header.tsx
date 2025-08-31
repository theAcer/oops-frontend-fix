"use client"

import { useAuth } from "@/contexts/auth-context"
import { Button } from "@/components/ui/button"
import { LogOut, User } from "lucide-react"
import { ThemeToggle } from "@/components/theme-toggle"
import { cn } from "@/lib/utils"

interface HeaderProps {
  isSidebarCollapsed: boolean;
}

export function Header({ isSidebarCollapsed }: HeaderProps) {
  const { user, logout } = useAuth()

  return (
    <header className={cn(
      "h-16 bg-card/70 backdrop-blur-lg border-b border-gray-200 flex items-center justify-between px-6 dark:border-gray-700 transition-all duration-300",
      // Removed conditional padding, using consistent px-6
    )}>
      <div className="flex items-center space-x-4">
        <h2 className="text-lg font-semibold text-gray-900 dark:text-gray-100">Welcome back, {user?.name}</h2>
      </div>

      <div className="flex items-center space-x-4">
        <div className="flex items-center space-x-2 text-sm text-gray-600 dark:text-gray-300">
          <User className="h-4 w-4" />
          <span>{user?.email}</span>
        </div>

        <ThemeToggle />

        <Button variant="outline" size="sm" onClick={logout} className="flex items-center space-x-2 bg-transparent dark:text-gray-300 dark:hover:bg-gray-700 dark:border-gray-600">
          <LogOut className="h-4 w-4" />
          <span>Logout</span>
        </Button>
      </div>
    </header>
  )
}