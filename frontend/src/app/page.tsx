import Link from "next/link"
import { ArrowRight, BarChart3, Users, Zap } from "lucide-react"
import { BlurredCard } from "@/components/blurred-card"
import { AnimatedButton } from "@/components/animated-button"
import { CardContent } from "@/components/ui/card"

export default function HomePage() {
  return (
    <div className="min-h-screen flex flex-col items-center justify-center py-16 bg-background text-foreground">
      <div className="container mx-auto px-4 text-center mb-16">
        <h1 className="text-5xl md:text-6xl font-bold mb-6 leading-tight">
          Zidisha <span className="text-primary">Loyalty</span> Platform
        </h1>
        <p className="text-lg md:text-xl text-muted-foreground mb-10 max-w-3xl mx-auto">
          AI-powered customer loyalty and engagement platform for merchants. Boost customer retention, increase
          revenue, and grow your business with intelligent insights.
        </p>
        <div className="flex flex-col sm:flex-row justify-center space-y-4 sm:space-y-0 sm:space-x-4">
          <AnimatedButton size="lg" className="text-lg px-8 py-4">
            <Link href="/dashboard">
              Get Started
              <ArrowRight className="ml-2 h-5 w-5" />
            </Link>
          </AnimatedButton>
          <AnimatedButton size="lg" variant="outline" className="text-lg px-8 py-4">
            <Link href="/register-merchant">
              Register as Merchant
              <ArrowRight className="ml-2 h-5 w-5" />
            </Link>
          </AnimatedButton>
        </div>
      </div>

      <div className="container mx-auto px-4 grid md:grid-cols-3 gap-8">
        <BlurredCard className="shadow-lg hover:shadow-xl transition-all duration-300">
          <CardContent className="p-8 flex flex-col items-center text-center">
            <div className="w-12 h-12 bg-brand-primary/10 rounded-lg flex items-center justify-center mb-4">
              <BarChart3 className="h-6 w-6 text-brand-primary" />
            </div>
            <h3 className="text-xl font-semibold mb-3 text-card-foreground">Advanced Analytics</h3>
            <p className="text-muted-foreground">
              Real-time insights into customer behavior, revenue trends, and business performance.
            </p>
          </CardContent>
        </BlurredCard>

        <BlurredCard className="shadow-lg hover:shadow-xl transition-all duration-300">
          <CardContent className="p-8 flex flex-col items-center text-center">
            <div className="w-12 h-12 bg-success/10 rounded-lg flex items-center justify-center mb-4">
              <Users className="h-6 w-6 text-success" />
            </div>
            <h3 className="text-xl font-semibold mb-3 text-card-foreground">Customer Management</h3>
            <p className="text-muted-foreground">
              Comprehensive customer profiles with loyalty tracking and engagement history.
            </p>
          </CardContent>
        </BlurredCard>

        <BlurredCard className="shadow-lg hover:shadow-xl transition-all duration-300">
          <CardContent className="p-8 flex flex-col items-center text-center">
            <div className="w-12 h-12 bg-brand-secondary/10 rounded-lg flex items-center justify-center mb-4">
              <Zap className="h-6 w-6 text-brand-secondary" />
            </div>
            <h3 className="text-xl font-semibold mb-3 text-card-foreground">AI Recommendations</h3>
            <p className="text-muted-foreground">
              Intelligent customer insights, churn prediction, and personalized marketing campaigns.
            </p>
          </CardContent>
        </BlurredCard>
      </div>
    </div>
  )
}