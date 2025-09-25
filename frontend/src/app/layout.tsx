import type React from "react"
import type { Metadata } from "next"
import { Inter } from "next/font/google"
import { AuthProvider } from "@/contexts/auth-context"
import { ThemeProvider } from "@/contexts/theme-context"
import { ThemeWrapper } from "@/components/theme-wrapper"
import { Toaster } from "react-hot-toast"
import "./globals.css"
import "./radix-select.css"

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
      <body className={inter.className} suppressHydrationWarning={true}>
        <ThemeProvider>
          <ThemeWrapper>
            <AuthProvider>
              {children}
              <Toaster
                position="top-right"
                toastOptions={{
                  duration: 4000,
                  style: {
                    background: 'hsl(var(--background))',
                    color: 'hsl(var(--foreground))',
                    border: '1px solid hsl(var(--border))',
                  },
                  success: {
                    style: {
                      border: '1px solid hsl(var(--primary))',
                    },
                  },
                  error: {
                    style: {
                      border: '1px solid hsl(var(--destructive))',
                    },
                  },
                }}
              />
            </AuthProvider>
          </ThemeWrapper>
        </ThemeProvider>
      </body>
    </html>
  )
}