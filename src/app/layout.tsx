import type React from "react"
import type { Metadata } from "next"
import { Inter } from "next/font/google"
import { AuthProvider } from "@/contexts/auth-context"
import { ThemeProvider } from "@/contexts/theme-context"
import { ThemeWrapper } from "@/components/theme-wrapper"
import "./globals.css"

const inter = Inter({ subsets: ["latin"] })

export const metadata: Metadata = {
  title: "Zidisha - Loyalty Platform",
  description: "AI-powered loyalty and customer engagement platform",
}

export default function RootLayout({
  children,
}: {
  children: React.ReactNode
}) {
  return (
    <html lang="en" suppressHydrationWarning>
      <body className={inter.className}>
        <ThemeProvider>
          <ThemeWrapper>
            <AuthProvider>{children}</AuthProvider>
          </ThemeWrapper>
        </ThemeProvider>
      </body>
    </html>
  )
}