"use client"

import type React from "react"

import { ProtectedRoute } from "@/components/auth/protected-route"
import { Sidebar } from "./sidebar"
import { Header } from "./header"

interface DashboardLayoutProps {
  children: React.ReactNode
}

export function DashboardLayout({ children }: DashboardLayoutProps) {
  // Removed isSidebarCollapsed state and toggleSidebar function

  return (
    <ProtectedRoute>
      <div className="h-screen flex">
        <Sidebar /> {/* No longer passing isCollapsed or toggleSidebar */}
        <div className="flex-1 flex flex-col overflow-hidden transition-all duration-300">
          <Header /> {/* No longer passing isSidebarCollapsed */}
          <main className="flex-1 overflow-y-auto p-6">{children}</main>
        </div>
      </div>
    </ProtectedRoute>
  )
}