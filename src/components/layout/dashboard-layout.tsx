"use client"

import type React from "react"
import { useState } from "react"

import { ProtectedRoute } from "@/components/auth/protected-route"
import { Sidebar } from "./sidebar"
import { Header } from "./header"
import { cn } from "@/lib/utils"

interface DashboardLayoutProps {
  children: React.ReactNode
}

export function DashboardLayout({ children }: DashboardLayoutProps) {
  const [isSidebarCollapsed, setIsSidebarCollapsed] = useState(false)

  const toggleSidebar = () => {
    setIsSidebarCollapsed(!isSidebarCollapsed)
  }

  return (
    <ProtectedRoute>
      <div className="h-screen flex bg-background"> {/* Ensure background is applied */}
        <Sidebar isCollapsed={isSidebarCollapsed} />
        <div className={cn(
          "flex-1 flex flex-col overflow-hidden transition-all duration-300",
          isSidebarCollapsed ? "ml-16" : "ml-64"
        )}>
          <Header toggleSidebar={toggleSidebar} isSidebarCollapsed={isSidebarCollapsed} />
          <main className="flex-1 overflow-y-auto p-6 bg-background">{children}</main> {/* Ensure main content area has background */}
        </div>
      </div>
    </ProtectedRoute>
  )
}