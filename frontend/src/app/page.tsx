import Link from "next/link"
import { ArrowRight, BarChart3, Users, Zap } from "lucide-react"

export default function HomePage() {
  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-50 to-indigo-100">
      <div className="container mx-auto px-4 py-16">
        <div className="text-center mb-16">
          <h1 className="text-5xl font-bold text-gray-900 mb-6">Zidisha Loyalty Platform</h1>
          <p className="text-xl text-gray-600 mb-8 max-w-3xl mx-auto">
            AI-powered customer loyalty and engagement platform for merchants. Boost customer retention, increase
            revenue, and grow your business with intelligent insights.
          </p>
          <Link
            href="/dashboard"
            className="inline-flex items-center px-8 py-4 bg-blue-600 text-white font-semibold rounded-lg hover:bg-blue-700 transition-colors"
          >
            Get Started
            <ArrowRight className="ml-2 h-5 w-5" />
          </Link>
        </div>

        <div className="grid md:grid-cols-3 gap-8 mb-16">
          <div className="bg-white p-8 rounded-xl shadow-lg">
            <div className="w-12 h-12 bg-blue-100 rounded-lg flex items-center justify-center mb-4">
              <BarChart3 className="h-6 w-6 text-blue-600" />
            </div>
            <h3 className="text-xl font-semibold mb-3">Advanced Analytics</h3>
            <p className="text-gray-600">
              Real-time insights into customer behavior, revenue trends, and business performance.
            </p>
          </div>

          <div className="bg-white p-8 rounded-xl shadow-lg">
            <div className="w-12 h-12 bg-green-100 rounded-lg flex items-center justify-center mb-4">
              <Users className="h-6 w-6 text-green-600" />
            </div>
            <h3 className="text-xl font-semibold mb-3">Customer Management</h3>
            <p className="text-gray-600">
              Comprehensive customer profiles with loyalty tracking and engagement history.
            </p>
          </div>

          <div className="bg-white p-8 rounded-xl shadow-lg">
            <div className="w-12 h-12 bg-purple-100 rounded-lg flex items-center justify-center mb-4">
              <Zap className="h-6 w-6 text-purple-600" />
            </div>
            <h3 className="text-xl font-semibold mb-3">AI Recommendations</h3>
            <p className="text-gray-600">
              Intelligent customer insights, churn prediction, and personalized marketing campaigns.
            </p>
          </div>
        </div>
      </div>
    </div>
  )
}
