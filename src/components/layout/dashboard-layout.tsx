"use client"

import type React from "react"
import { useState } from "react" // Import useState

import { ProtectedRoute } from "@/components/auth/protected-route"
import { Sidebar } from "./sidebar"
import { Header } from "./header"
import { cn } from "@/lib/utils" // Import cn for conditional classes

interface DashboardLayoutProps {
  children: React.ReactNode
}

export function DashboardLayout({ children }: DashboardLayoutProps) {
  const [isSidebarCollapsed, setIsSidebarCollapsed] = useState(false) // State for sidebar collapse

  const toggleSidebar = () => {
    setIsSidebarCollapsed(!isSidebarCollapsed)
  }

  return (
    <ProtectedRoute>
      <div className="h-screen flex">
        <Sidebar isCollapsed={isSidebarCollapsed} /> {/* Pass isCollapsed prop */}
        <div className={cn(
          "flex-1 flex flex-col overflow-hidden transition-all duration-300",
          isSidebarCollapsed ? "ml-16" : "ml-64" // Adjust margin based on sidebar state
        )}>
          <Header toggleSidebar={toggleSidebar} isSidebarCollapsed={isSidebarCollapsed} /> {/* Pass toggleSidebar and isSidebarCollapsed */}
          <main className="flex-1 overflow-y-auto p-6">{children}</main>
        </div>
      </div>
    </ProtectedRoute>
  )
}