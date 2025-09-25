/**
 * M-Pesa Channel Onboarding Component
 * 
 * Multi-step wizard for merchants to add M-Pesa channels to their loyalty platform.
 * Supports PayBill, Till, and Buy Goods channels with secure credential handling.
 */

'use client'

import { useState, useEffect } from 'react'
import { useRouter } from 'next/navigation'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import { Label } from '@/components/ui/label'
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select'
import { Textarea } from '@/components/ui/textarea'
import { Switch } from '@/components/ui/switch'
import { Badge } from '@/components/ui/badge'
import { Alert, AlertDescription } from '@/components/ui/alert'
import { Progress } from '@/components/ui/progress'
import { Separator } from '@/components/ui/separator'
import { CheckCircle, AlertCircle, Loader2, Plus, Trash2, Info } from 'lucide-react'
import { toast } from 'sonner'

interface ChannelData {
  name: string
  shortcode: string
  channel_type: 'paybill' | 'till' | 'buygoods'
  environment: 'sandbox' | 'production'
  consumer_key: string
  consumer_secret: string
  passkey?: string
  validation_url?: string
  confirmation_url?: string
  callback_url?: string
  account_mapping?: Record<string, string>
  is_primary: boolean
}

interface OnboardingStep {
  id: string
  title: string
  description: string
  completed: boolean
}

const ONBOARDING_STEPS: OnboardingStep[] = [
  {
    id: 'basic-info',
    title: 'Basic Information',
    description: 'Channel name, shortcode, and type',
    completed: false
  },
  {
    id: 'credentials',
    title: 'M-Pesa Credentials',
    description: 'Consumer key, secret, and passkey',
    completed: false
  },
  {
    id: 'urls',
    title: 'Callback URLs',
    description: 'Validation and confirmation URLs',
    completed: false
  },
  {
    id: 'account-mapping',
    title: 'Account Mapping',
    description: 'PayBill account reference mapping',
    completed: false
  },
  {
    id: 'verification',
    title: 'Verification',
    description: 'Test and verify channel',
    completed: false
  }
]

export default function ChannelOnboarding() {
  const router = useRouter()
  const [currentStep, setCurrentStep] = useState(0)
  const [loading, setLoading] = useState(false)
  const [channelData, setChannelData] = useState<ChannelData>({
    name: '',
    shortcode: '',
    channel_type: 'paybill',
    environment: 'sandbox',
    consumer_key: '',
    consumer_secret: '',
    passkey: '',
    validation_url: '',
    confirmation_url: '',
    callback_url: '',
    account_mapping: { default: 'loyalty' },
    is_primary: false
  })
  const [steps, setSteps] = useState(ONBOARDING_STEPS)
  const [verificationResult, setVerificationResult] = useState<any>(null)

  const updateStepCompletion = (stepIndex: number, completed: boolean) => {
    setSteps(prev => prev.map((step, index) => 
      index === stepIndex ? { ...step, completed } : step
    ))
  }

  const validateCurrentStep = (): boolean => {
    switch (currentStep) {
      case 0: // Basic Info
        return !!(channelData.name && channelData.shortcode && channelData.channel_type)
      case 1: // Credentials
        return !!(channelData.consumer_key && channelData.consumer_secret)
      case 2: // URLs
        return channelData.channel_type === 'till' || 
               !!(channelData.validation_url && channelData.confirmation_url)
      case 3: // Account Mapping
        return channelData.channel_type !== 'paybill' || 
               Object.keys(channelData.account_mapping || {}).length > 0
      default:
        return true
    }
  }

  const handleNext = () => {
    if (validateCurrentStep()) {
      updateStepCompletion(currentStep, true)
      if (currentStep < steps.length - 1) {
        setCurrentStep(currentStep + 1)
      }
    } else {
      toast.error('Please fill in all required fields')
    }
  }

  const handlePrevious = () => {
    if (currentStep > 0) {
      setCurrentStep(currentStep - 1)
    }
  }

  const createChannel = async () => {
    setLoading(true)
    try {
      const response = await fetch('/api/v1/mpesa-channels/', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${localStorage.getItem('token')}`
        },
        body: JSON.stringify(channelData)
      })

      if (!response.ok) {
        throw new Error('Failed to create channel')
      }

      const channel = await response.json()
      toast.success('M-Pesa channel created successfully!')
      
      // Auto-verify if in sandbox
      if (channelData.environment === 'sandbox') {
        await verifyChannel(channel.id)
      }
      
      router.push('/dashboard/mpesa-channels')
    } catch (error) {
      toast.error('Failed to create channel')
      console.error(error)
    } finally {
      setLoading(false)
    }
  }

  const verifyChannel = async (channelId: number) => {
    try {
      const response = await fetch(`/api/v1/mpesa-channels/${channelId}/verify`, {
        method: 'POST',
        headers: {
          'Authorization': `Bearer ${localStorage.getItem('token')}`
        }
      })

      const result = await response.json()
      setVerificationResult(result)
      
      if (result.verified) {
        toast.success('Channel verified successfully!')
        updateStepCompletion(4, true)
      } else {
        toast.error('Channel verification failed')
      }
    } catch (error) {
      toast.error('Verification failed')
      console.error(error)
    }
  }

  const addAccountMapping = () => {
    const newKey = `account_${Object.keys(channelData.account_mapping || {}).length + 1}`
    setChannelData(prev => ({
      ...prev,
      account_mapping: {
        ...prev.account_mapping,
        [newKey]: ''
      }
    }))
  }

  const removeAccountMapping = (key: string) => {
    if (key === 'default') return // Can't remove default mapping
    
    setChannelData(prev => {
      const newMapping = { ...prev.account_mapping }
      delete newMapping[key]
      return { ...prev, account_mapping: newMapping }
    })
  }

  const updateAccountMapping = (oldKey: string, newKey: string, value: string) => {
    setChannelData(prev => {
      const newMapping = { ...prev.account_mapping }
      if (oldKey !== newKey) {
        delete newMapping[oldKey]
      }
      newMapping[newKey] = value
      return { ...prev, account_mapping: newMapping }
    })
  }

  const renderStepContent = () => {
    switch (currentStep) {
      case 0: // Basic Information
        return (
          <div className="space-y-6">
            <div className="space-y-2">
              <Label htmlFor="name">Channel Name *</Label>
              <Input
                id="name"
                placeholder="e.g., Main PayBill, Shop Till"
                value={channelData.name}
                onChange={(e) => setChannelData(prev => ({ ...prev, name: e.target.value }))}
              />
              <p className="text-sm text-muted-foreground">
                A friendly name to identify this channel
              </p>
            </div>

            <div className="space-y-2">
              <Label htmlFor="shortcode">M-Pesa Shortcode *</Label>
              <Input
                id="shortcode"
                placeholder="e.g., 174379"
                value={channelData.shortcode}
                onChange={(e) => setChannelData(prev => ({ ...prev, shortcode: e.target.value }))}
              />
              <p className="text-sm text-muted-foreground">
                Your M-Pesa business shortcode (numbers only)
              </p>
            </div>

            <div className="space-y-2">
              <Label htmlFor="channel_type">Channel Type *</Label>
              <Select
                value={channelData.channel_type}
                onValueChange={(value: 'paybill' | 'till' | 'buygoods') => 
                  setChannelData(prev => ({ ...prev, channel_type: value }))
                }
              >
                <SelectTrigger>
                  <SelectValue />
                </SelectTrigger>
                <SelectContent>
                  <SelectItem value="paybill">PayBill (with account numbers)</SelectItem>
                  <SelectItem value="till">Till Number</SelectItem>
                  <SelectItem value="buygoods">Buy Goods</SelectItem>
                </SelectContent>
              </Select>
            </div>

            <div className="space-y-2">
              <Label htmlFor="environment">Environment *</Label>
              <Select
                value={channelData.environment}
                onValueChange={(value: 'sandbox' | 'production') => 
                  setChannelData(prev => ({ ...prev, environment: value }))
                }
              >
                <SelectTrigger>
                  <SelectValue />
                </SelectTrigger>
                <SelectContent>
                  <SelectItem value="sandbox">Sandbox (Testing)</SelectItem>
                  <SelectItem value="production">Production (Live)</SelectItem>
                </SelectContent>
              </Select>
              <p className="text-sm text-muted-foreground">
                Start with sandbox for testing, then switch to production
              </p>
            </div>

            <div className="flex items-center space-x-2">
              <Switch
                id="is_primary"
                checked={channelData.is_primary}
                onCheckedChange={(checked) => 
                  setChannelData(prev => ({ ...prev, is_primary: checked }))
                }
              />
              <Label htmlFor="is_primary">Make this the primary channel</Label>
            </div>
          </div>
        )

      case 1: // Credentials
        return (
          <div className="space-y-6">
            <Alert>
              <Info className="h-4 w-4" />
              <AlertDescription>
                Your credentials are encrypted and stored securely. They're never shared or visible to anyone.
              </AlertDescription>
            </Alert>

            <div className="space-y-2">
              <Label htmlFor="consumer_key">Consumer Key *</Label>
              <Input
                id="consumer_key"
                type="password"
                placeholder="Your M-Pesa consumer key"
                value={channelData.consumer_key}
                onChange={(e) => setChannelData(prev => ({ ...prev, consumer_key: e.target.value }))}
              />
            </div>

            <div className="space-y-2">
              <Label htmlFor="consumer_secret">Consumer Secret *</Label>
              <Input
                id="consumer_secret"
                type="password"
                placeholder="Your M-Pesa consumer secret"
                value={channelData.consumer_secret}
                onChange={(e) => setChannelData(prev => ({ ...prev, consumer_secret: e.target.value }))}
              />
            </div>

            <div className="space-y-2">
              <Label htmlFor="passkey">Passkey (for STK Push)</Label>
              <Input
                id="passkey"
                type="password"
                placeholder="Your M-Pesa passkey (optional)"
                value={channelData.passkey}
                onChange={(e) => setChannelData(prev => ({ ...prev, passkey: e.target.value }))}
              />
              <p className="text-sm text-muted-foreground">
                Required only if you plan to use STK Push (Lipa Na M-Pesa Online)
              </p>
            </div>
          </div>
        )

      case 2: // URLs
        return (
          <div className="space-y-6">
            {channelData.channel_type === 'till' ? (
              <Alert>
                <Info className="h-4 w-4" />
                <AlertDescription>
                  Till numbers don't require callback URLs. You can skip this step.
                </AlertDescription>
              </Alert>
            ) : (
              <>
                <div className="space-y-2">
                  <Label htmlFor="validation_url">Validation URL *</Label>
                  <Input
                    id="validation_url"
                    placeholder="https://your-api.com/mpesa/validation"
                    value={channelData.validation_url}
                    onChange={(e) => setChannelData(prev => ({ ...prev, validation_url: e.target.value }))}
                  />
                  <p className="text-sm text-muted-foreground">
                    Called by M-Pesa to validate incoming transactions
                  </p>
                </div>

                <div className="space-y-2">
                  <Label htmlFor="confirmation_url">Confirmation URL *</Label>
                  <Input
                    id="confirmation_url"
                    placeholder="https://your-api.com/mpesa/confirmation"
                    value={channelData.confirmation_url}
                    onChange={(e) => setChannelData(prev => ({ ...prev, confirmation_url: e.target.value }))}
                  />
                  <p className="text-sm text-muted-foreground">
                    Called by M-Pesa to confirm successful transactions
                  </p>
                </div>

                <div className="space-y-2">
                  <Label htmlFor="callback_url">STK Push Callback URL</Label>
                  <Input
                    id="callback_url"
                    placeholder="https://your-api.com/mpesa/stk-callback"
                    value={channelData.callback_url}
                    onChange={(e) => setChannelData(prev => ({ ...prev, callback_url: e.target.value }))}
                  />
                  <p className="text-sm text-muted-foreground">
                    Called for STK Push transaction results (optional)
                  </p>
                </div>
              </>
            )}
          </div>
        )

      case 3: // Account Mapping
        return (
          <div className="space-y-6">
            {channelData.channel_type !== 'paybill' ? (
              <Alert>
                <Info className="h-4 w-4" />
                <AlertDescription>
                  Account mapping is only needed for PayBill channels. You can skip this step.
                </AlertDescription>
              </Alert>
            ) : (
              <>
                <div className="space-y-4">
                  <div>
                    <h3 className="text-lg font-medium">Account Reference Mapping</h3>
                    <p className="text-sm text-muted-foreground">
                      Map account references to different loyalty programs or customer segments
                    </p>
                  </div>

                  {Object.entries(channelData.account_mapping || {}).map(([key, value]) => (
                    <div key={key} className="flex items-center space-x-2">
                      <Input
                        placeholder="Account reference (e.g., VIP*, GOLD001)"
                        value={key}
                        onChange={(e) => updateAccountMapping(key, e.target.value, value)}
                        disabled={key === 'default'}
                      />
                      <span>→</span>
                      <Input
                        placeholder="Loyalty program (e.g., vip_program)"
                        value={value}
                        onChange={(e) => updateAccountMapping(key, key, e.target.value)}
                      />
                      {key !== 'default' && (
                        <Button
                          variant="outline"
                          size="icon"
                          onClick={() => removeAccountMapping(key)}
                        >
                          <Trash2 className="h-4 w-4" />
                        </Button>
                      )}
                    </div>
                  ))}

                  <Button
                    variant="outline"
                    onClick={addAccountMapping}
                    className="w-full"
                  >
                    <Plus className="h-4 w-4 mr-2" />
                    Add Account Mapping
                  </Button>
                </div>

                <Alert>
                  <Info className="h-4 w-4" />
                  <AlertDescription>
                    Use * for wildcards (e.g., VIP* matches VIP001, VIP002, etc.)
                  </AlertDescription>
                </Alert>
              </>
            )}
          </div>
        )

      case 4: // Verification
        return (
          <div className="space-y-6">
            <div className="text-center">
              <h3 className="text-lg font-medium">Ready to Create Channel</h3>
              <p className="text-muted-foreground">
                Review your configuration and create the M-Pesa channel
              </p>
            </div>

            <Card>
              <CardHeader>
                <CardTitle>Channel Summary</CardTitle>
              </CardHeader>
              <CardContent className="space-y-4">
                <div className="grid grid-cols-2 gap-4">
                  <div>
                    <Label className="text-sm font-medium">Name</Label>
                    <p className="text-sm">{channelData.name}</p>
                  </div>
                  <div>
                    <Label className="text-sm font-medium">Shortcode</Label>
                    <p className="text-sm">{channelData.shortcode}</p>
                  </div>
                  <div>
                    <Label className="text-sm font-medium">Type</Label>
                    <Badge variant="secondary">{channelData.channel_type}</Badge>
                  </div>
                  <div>
                    <Label className="text-sm font-medium">Environment</Label>
                    <Badge variant={channelData.environment === 'production' ? 'destructive' : 'default'}>
                      {channelData.environment}
                    </Badge>
                  </div>
                </div>

                {verificationResult && (
                  <div className="mt-4 p-4 rounded-lg bg-muted">
                    <div className="flex items-center space-x-2">
                      {verificationResult.verified ? (
                        <CheckCircle className="h-5 w-5 text-green-500" />
                      ) : (
                        <AlertCircle className="h-5 w-5 text-red-500" />
                      )}
                      <span className="font-medium">
                        {verificationResult.verified ? 'Verification Successful' : 'Verification Failed'}
                      </span>
                    </div>
                    {verificationResult.error && (
                      <p className="text-sm text-muted-foreground mt-2">
                        {verificationResult.error}
                      </p>
                    )}
                  </div>
                )}
              </CardContent>
            </Card>

            <Button
              onClick={createChannel}
              disabled={loading}
              className="w-full"
              size="lg"
            >
              {loading ? (
                <>
                  <Loader2 className="h-4 w-4 mr-2 animate-spin" />
                  Creating Channel...
                </>
              ) : (
                'Create M-Pesa Channel'
              )}
            </Button>
          </div>
        )

      default:
        return null
    }
  }

  return (
    <div className="max-w-4xl mx-auto p-6">
      <div className="mb-8">
        <h1 className="text-3xl font-bold">Add M-Pesa Channel</h1>
        <p className="text-muted-foreground">
          Connect your M-Pesa business account to start processing loyalty transactions
        </p>
      </div>

      {/* Progress Indicator */}
      <div className="mb-8">
        <div className="flex items-center justify-between mb-4">
          {steps.map((step, index) => (
            <div
              key={step.id}
              className={`flex items-center ${index < steps.length - 1 ? 'flex-1' : ''}`}
            >
              <div className="flex items-center space-x-2">
                <div
                  className={`w-8 h-8 rounded-full flex items-center justify-center text-sm font-medium ${
                    index === currentStep
                      ? 'bg-primary text-primary-foreground'
                      : step.completed
                      ? 'bg-green-500 text-white'
                      : 'bg-muted text-muted-foreground'
                  }`}
                >
                  {step.completed ? (
                    <CheckCircle className="h-4 w-4" />
                  ) : (
                    index + 1
                  )}
                </div>
                <div className="hidden sm:block">
                  <p className="text-sm font-medium">{step.title}</p>
                  <p className="text-xs text-muted-foreground">{step.description}</p>
                </div>
              </div>
              {index < steps.length - 1 && (
                <Separator className="flex-1 mx-4" />
              )}
            </div>
          ))}
        </div>
        <Progress value={((currentStep + 1) / steps.length) * 100} className="w-full" />
      </div>

      {/* Step Content */}
      <Card>
        <CardHeader>
          <CardTitle>{steps[currentStep].title}</CardTitle>
          <CardDescription>{steps[currentStep].description}</CardDescription>
        </CardHeader>
        <CardContent>
          {renderStepContent()}
        </CardContent>
      </Card>

      {/* Navigation */}
      <div className="flex justify-between mt-6">
        <Button
          variant="outline"
          onClick={handlePrevious}
          disabled={currentStep === 0}
        >
          Previous
        </Button>
        
        {currentStep < steps.length - 1 ? (
          <Button
            onClick={handleNext}
            disabled={!validateCurrentStep()}
          >
            Next
          </Button>
        ) : null}
      </div>
    </div>
  )
}
