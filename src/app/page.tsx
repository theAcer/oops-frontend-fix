import Link from "next/link"
import { ArrowRight, BarChart3, Users, Zap } from "lucide-react"
import { Button } from "@/components/ui/button"
import { Card, CardContent } from "@/components/ui/card"
import { AnimatedButton } from "@/components/animated-button" // Import AnimatedButton

export default function HomePage() {
  return (
    <div className="min-h-screen"> {/* Removed bg-[--gradient-subtle] as ThemeWrapper handles it */}
      <div className="container mx-auto px-4 py-16">
        <div className="text-center mb-16">
          <h1 className="text-5xl font-bold text-foreground mb-6">Zidisha Loyalty Platform</h1>
          <p className="text-xl text-muted-foreground mb-8 max-w-3xl mx-auto">
            AI-powered customer loyalty and engagement platform for merchants. Boost customer retention, increase
            revenue, and grow your business with intelligent insights.
          </p>
          <div className="flex justify-center space-x-4">
            <AnimatedButton size="lg" asChild className="text-lg px-8 py-4">
              <Link href="/dashboard">
                Get Started
                <ArrowRight className="ml-2 h-5 w-5" />
              </Link>
            </AnimatedButton>
            <AnimatedButton size="lg" variant="outline" asChild className="text-lg px-8 py-4">
              <Link href="/register-merchant">
                Register as Merchant
                <ArrowRight className="ml-2 h-5 w-5" />
              </Link>
            </AnimatedButton>
          </div>
        </div>

        <div className="grid md:grid-cols-3 gap-8 mb-16">
          <Card className="shadow-[--shadow-elegant] hover:shadow-[--shadow-glow] transition-all duration-300">
            <CardContent className="p-8">
              <div className="w-12 h-12 bg-brand-primary/10 rounded-lg flex items-center justify-center mb-4">
                <BarChart3 className="h-6 w-6 text-brand-primary" />
              </div>
              <h3 className="text-xl font-semibold mb-3 text-card-foreground">Advanced Analytics</h3>
              <p className="text-muted-foreground">
                Real-time insights into customer behavior, revenue trends, and business performance.
              </p>
            </CardContent>
          </Card>

          <Card className="shadow-[--shadow-elegant] hover:shadow-[--shadow-glow] transition-all duration-300">
            <CardContent className="p-8">
              <div className="w-12 h-12 bg-success/10 rounded-lg flex items-center justify-center mb-4">
                <Users className="h-6 w-6 text-success" />
              </div>
              <h3 className="text-xl font-semibold mb-3 text-card-foreground">Customer Management</h3>
              <p className="text-muted-foreground">
                Comprehensive customer profiles with loyalty tracking and engagement history.
              </p>
            </CardContent>
          </Card>

          <Card className="shadow-[--shadow-elegant] hover:shadow-[--shadow-glow] transition-all duration-300">
            <CardContent className="p-8">
              <div className="w-12 h-12 bg-brand-secondary/10 rounded-lg flex items-center justify-center mb-4">
                <Zap className="h-6 w-6 text-brand-secondary" />
              </div>
              <h3 className="text-xl font-semibold mb-3 text-card-foreground">AI Recommendations</h3>
              <p className="text-muted-foreground">
                Intelligent customer insights, churn prediction, and personalized marketing campaigns.
              </p>
            </CardContent>
          </Card>
        </div>
      </div>
    </div>
  )
}