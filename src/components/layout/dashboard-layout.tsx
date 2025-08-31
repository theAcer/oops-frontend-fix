"use client"

import type React from "react"
import { useState } from "react"

import { ProtectedRoute } from "@/components/auth/protected-route"
import { Sidebar } from "./sidebar"
import { Header } from "./header"

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
      <div className="h-screen flex"> {/* Removed flex-row, just flex */}
        <Sidebar isCollapsed={isSidebarCollapsed} toggleSidebar={toggleSidebar} />
        <div className="flex-1 flex flex-col overflow-hidden transition-all duration-300"> {/* Removed ml- classes */}
          <Header isSidebarCollapsed={isSidebarCollapsed} />
          <main className="flex-1 overflow-y-auto p-6">{children}</main>
        </div>
      </div>
    </ProtectedRoute>
  )
}