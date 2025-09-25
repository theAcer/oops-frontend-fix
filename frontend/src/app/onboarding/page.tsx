"use client"

import React, { useState, useEffect } from "react"
import { useRouter } from "next/navigation"
import { useAuth } from "@/contexts/auth-context"
import { MerchantOnboardingWizard } from "@/components/onboarding/MerchantOnboardingWizard"
import { OnboardingProvider } from "@/contexts/onboarding-context"
import { BlurredCard } from "@/components/blurred-card"
import { CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card"
import { Progress } from "@/components/ui/progress"
import { CheckCircle, Building, CreditCard, Settings, Rocket } from "lucide-react"

const ONBOARDING_STEPS = [
  {
    id: "business-info",
    title: "Business Information",
    description: "Tell us about your business",
    icon: Building,
    completed: false
  },
  {
    id: "mpesa-setup",
    title: "M-Pesa Integration",
    description: "Connect your M-Pesa channels",
    icon: CreditCard,
    completed: false
  },
  {
    id: "loyalty-config",
    title: "Loyalty Program",
    description: "Configure your loyalty program",
    icon: Settings,
    completed: false
  },
  {
    id: "launch",
    title: "Launch",
    description: "Review and launch your platform",
    icon: Rocket,
    completed: false
  }
]

export default function OnboardingPage() {
  const { user } = useAuth()
  const router = useRouter()
  const [currentStep, setCurrentStep] = useState(0)
  const [completedSteps, setCompletedSteps] = useState<string[]>([])

  // Redirect if user is already authenticated and has completed onboarding
  useEffect(() => {
    if (user?.merchant_id && user?.onboarding_completed) {
      router.push("/dashboard")
    }
  }, [user, router])

  const handleStepComplete = (stepId: string) => {
    setCompletedSteps(prev => [...prev, stepId])
    
    // Move to next step
    const nextStepIndex = currentStep + 1
    if (nextStepIndex < ONBOARDING_STEPS.length) {
      setCurrentStep(nextStepIndex)
    }
  }

  const handleOnboardingComplete = () => {
    // Redirect to dashboard after successful onboarding
    router.push("/dashboard")
  }

  const progressPercentage = ((completedSteps.length) / ONBOARDING_STEPS.length) * 100

  return (
    <OnboardingProvider>
      <div className="min-h-screen bg-gradient-to-br from-background via-background/95 to-primary/5">
        <div className="container mx-auto px-4 py-8">
          {/* Header */}
          <div className="text-center mb-8">
            <h1 className="text-4xl font-bold text-foreground mb-2">
              Welcome to Zidisha Loyalty Platform
            </h1>
            <p className="text-lg text-muted-foreground">
              Let's get your business set up with AI-powered customer loyalty
            </p>
          </div>

          {/* Progress Overview */}
          <BlurredCard className="max-w-4xl mx-auto mb-8">
            <CardHeader>
              <CardTitle className="flex items-center gap-2">
                <Building className="h-5 w-5" />
                Setup Progress
              </CardTitle>
              <CardDescription>
                Complete all steps to launch your loyalty platform
              </CardDescription>
            </CardHeader>
            <CardContent>
              <div className="mb-6">
                <div className="flex justify-between text-sm text-muted-foreground mb-2">
                  <span>Progress</span>
                  <span>{Math.round(progressPercentage)}% Complete</span>
                </div>
                <Progress value={progressPercentage} className="h-2" />
              </div>

              {/* Step Overview */}
              <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
                {ONBOARDING_STEPS.map((step, index) => {
                  const Icon = step.icon
                  const isCompleted = completedSteps.includes(step.id)
                  const isCurrent = index === currentStep
                  const isAccessible = index <= currentStep

                  return (
                    <div
                      key={step.id}
                      className={`
                        relative p-4 rounded-lg border transition-all duration-200
                        ${isCurrent 
                          ? "border-primary bg-primary/5 shadow-sm" 
                          : isCompleted 
                            ? "border-green-500 bg-green-50 dark:bg-green-950/20" 
                            : "border-border bg-background/50"
                        }
                        ${isAccessible ? "cursor-pointer hover:shadow-md" : "opacity-50"}
                      `}
                      onClick={() => isAccessible && setCurrentStep(index)}
                    >
                      <div className="flex items-center gap-3 mb-2">
                        {isCompleted ? (
                          <CheckCircle className="h-5 w-5 text-green-500" />
                        ) : (
                          <Icon className={`h-5 w-5 ${isCurrent ? "text-primary" : "text-muted-foreground"}`} />
                        )}
                        <span className={`font-medium ${isCurrent ? "text-primary" : isCompleted ? "text-green-700 dark:text-green-400" : "text-foreground"}`}>
                          {step.title}
                        </span>
                      </div>
                      <p className="text-sm text-muted-foreground">
                        {step.description}
                      </p>
                      
                      {/* Step number */}
                      <div className={`
                        absolute -top-2 -right-2 w-6 h-6 rounded-full text-xs font-bold
                        flex items-center justify-center
                        ${isCompleted 
                          ? "bg-green-500 text-white" 
                          : isCurrent 
                            ? "bg-primary text-primary-foreground" 
                            : "bg-muted text-muted-foreground"
                        }
                      `}>
                        {isCompleted ? "✓" : index + 1}
                      </div>
                    </div>
                  )
                })}
              </div>
            </CardContent>
          </BlurredCard>

          {/* Main Onboarding Wizard */}
          <div className="max-w-4xl mx-auto">
            <MerchantOnboardingWizard
              currentStep={ONBOARDING_STEPS[currentStep]}
              stepIndex={currentStep}
              totalSteps={ONBOARDING_STEPS.length}
              onStepComplete={handleStepComplete}
              onComplete={handleOnboardingComplete}
              completedSteps={completedSteps}
            />
          </div>
        </div>
      </div>
    </OnboardingProvider>
  )
}
