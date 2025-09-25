"use client"

import React, { useState } from "react"
import { useOnboarding } from "@/contexts/onboarding-context"
import { BlurredCard } from "@/components/blurred-card"
import { CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card"
import { Button } from "@/components/ui/button"
import { ArrowLeft, ArrowRight, CheckCircle } from "lucide-react"
import { BusinessInfoStep } from "./steps/BusinessInfoStep"
import { MpesaSetupStep } from "./steps/MpesaSetupStep"
import { LoyaltyConfigStep } from "./steps/LoyaltyConfigStep"
import { LaunchStep } from "./steps/LaunchStep"
import { toast } from "react-hot-toast"

interface OnboardingStep {
  id: string
  title: string
  description: string
  icon: React.ComponentType<any>
}

interface MerchantOnboardingWizardProps {
  currentStep: OnboardingStep
  stepIndex: number
  totalSteps: number
  onStepComplete: (stepId: string) => void
  onComplete: () => void
  completedSteps: string[]
}

export function MerchantOnboardingWizard({
  currentStep,
  stepIndex,
  totalSteps,
  onStepComplete,
  onComplete,
  completedSteps
}: MerchantOnboardingWizardProps) {
  const {
    validateBusinessInfo,
    validateMpesaChannels,
    validateLoyaltyProgram
  } = useOnboarding()
  
  const [isProcessing, setIsProcessing] = useState(false)

  const handleNext = async () => {
    setIsProcessing(true)
    
    try {
      let isValid = false
      
      // Validate current step
      switch (currentStep.id) {
        case "business-info":
          isValid = validateBusinessInfo()
          break
        case "mpesa-setup":
          isValid = validateMpesaChannels()
          break
        case "loyalty-config":
          isValid = validateLoyaltyProgram()
          break
        case "launch":
          isValid = true // Launch step handles its own validation
          break
        default:
          isValid = true
      }

      if (isValid) {
        // Mark current step as completed
        if (!completedSteps.includes(currentStep.id)) {
          onStepComplete(currentStep.id)
        }

        // If this is the last step, complete onboarding
        if (stepIndex === totalSteps - 1) {
          onComplete()
        }
      }
    } catch (error) {
      console.error("Error in onboarding step:", error)
      toast.error("An error occurred. Please try again.")
    } finally {
      setIsProcessing(false)
    }
  }

  const handleBack = () => {
    // This would be handled by the parent component
    // For now, we'll just show a message
    toast.error("Navigation handled by parent component")
  }

  const renderStepContent = () => {
    switch (currentStep.id) {
      case "business-info":
        return <BusinessInfoStep />
      case "mpesa-setup":
        return <MpesaSetupStep />
      case "loyalty-config":
        return <LoyaltyConfigStep />
      case "launch":
        return <LaunchStep onComplete={onComplete} />
      default:
        return <div>Unknown step</div>
    }
  }

  const isStepCompleted = completedSteps.includes(currentStep.id)
  const isLastStep = stepIndex === totalSteps - 1

  return (
    <BlurredCard className="w-full">
      <CardHeader>
        <div className="flex items-center justify-between">
          <div>
            <CardTitle className="flex items-center gap-2">
              <currentStep.icon className="h-5 w-5" />
              {currentStep.title}
              {isStepCompleted && (
                <CheckCircle className="h-5 w-5 text-green-500" />
              )}
            </CardTitle>
            <CardDescription className="mt-1">
              {currentStep.description}
            </CardDescription>
          </div>
          <div className="text-sm text-muted-foreground">
            Step {stepIndex + 1} of {totalSteps}
          </div>
        </div>
      </CardHeader>

      <CardContent>
        {/* Step Content */}
        <div className="mb-8">
          {renderStepContent()}
        </div>

        {/* Navigation */}
        <div className="flex items-center justify-between pt-6 border-t">
          <Button
            variant="outline"
            onClick={handleBack}
            disabled={stepIndex === 0 || isProcessing}
            className="flex items-center gap-2"
          >
            <ArrowLeft className="h-4 w-4" />
            Back
          </Button>

          <div className="flex items-center gap-2">
            {!isLastStep ? (
              <Button
                onClick={handleNext}
                disabled={isProcessing}
                className="flex items-center gap-2"
              >
                {isProcessing ? "Processing..." : "Continue"}
                <ArrowRight className="h-4 w-4" />
              </Button>
            ) : (
              <Button
                onClick={handleNext}
                disabled={isProcessing}
                className="flex items-center gap-2 bg-green-600 hover:bg-green-700"
              >
                {isProcessing ? "Launching..." : "Launch Platform"}
                <CheckCircle className="h-4 w-4" />
              </Button>
            )}
          </div>
        </div>
      </CardContent>
    </BlurredCard>
  )
}
