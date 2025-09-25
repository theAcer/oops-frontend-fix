"use client"

import React, { useState } from "react"
import { useOnboarding, type MpesaChannelData } from "@/contexts/onboarding-context"
import { Button } from "@/components/ui/button"
import { Input } from "@/components/ui/input"
import { Label } from "@/components/ui/label"
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select"
import { Switch } from "@/components/ui/switch"
import { Textarea } from "@/components/ui/textarea"
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card"
import { Badge } from "@/components/ui/badge"
import { Alert, AlertDescription } from "@/components/ui/alert"
import { Separator } from "@/components/ui/separator"
import { 
  CreditCard, 
  Plus, 
  Trash2, 
  Eye, 
  EyeOff, 
  Shield, 
  AlertTriangle,
  CheckCircle,
  Info,
  ExternalLink,
  Settings
} from "lucide-react"
import { toast } from "react-hot-toast"

const CHANNEL_TYPES = [
  {
    value: "paybill",
    label: "PayBill",
    description: "For businesses with a PayBill number. Supports account references.",
    icon: "💳"
  },
  {
    value: "till",
    label: "Till Number",
    description: "For businesses with a Till number. Simple payment collection.",
    icon: "🏪"
  },
  {
    value: "buygoods",
    label: "Buy Goods",
    description: "For online businesses. Supports e-commerce integration.",
    icon: "🛒"
  }
]

const ENVIRONMENTS = [
  {
    value: "sandbox",
    label: "Sandbox (Testing)",
    description: "Use for testing and development",
    color: "bg-yellow-100 text-yellow-800 dark:bg-yellow-900/20 dark:text-yellow-400"
  },
  {
    value: "production",
    label: "Production (Live)",
    description: "Use for real transactions",
    color: "bg-green-100 text-green-800 dark:bg-green-900/20 dark:text-green-400"
  }
]

export function MpesaSetupStep() {
  const { data, addMpesaChannel, updateMpesaChannel, removeMpesaChannel } = useOnboarding()
  const { mpesaChannels } = data
  
  const [showAddForm, setShowAddForm] = useState(mpesaChannels.length === 0)
  const [editingIndex, setEditingIndex] = useState<number | null>(null)
  const [showCredentials, setShowCredentials] = useState<Record<number, boolean>>({})
  const [newChannel, setNewChannel] = useState<MpesaChannelData>({
    name: "",
    shortcode: "",
    channel_type: "paybill",
    environment: "sandbox",
    consumer_key: "",
    consumer_secret: "",
    passkey: "",
    validation_url: "",
    confirmation_url: "",
    callback_url: "",
    account_mapping: {},
    is_primary: mpesaChannels.length === 0
  })

  const handleAddChannel = () => {
    // Validate required fields
    if (!newChannel.name.trim()) {
      toast.error("Channel name is required")
      return
    }
    
    if (!newChannel.shortcode.trim()) {
      toast.error("Shortcode is required")
      return
    }
    
    if (!newChannel.consumer_key.trim()) {
      toast.error("Consumer key is required")
      return
    }
    
    if (!newChannel.consumer_secret.trim()) {
      toast.error("Consumer secret is required")
      return
    }

    // If this is the first channel, make it primary
    if (mpesaChannels.length === 0) {
      newChannel.is_primary = true
    }

    // If setting as primary, unset other primary channels
    if (newChannel.is_primary) {
      mpesaChannels.forEach((_, index) => {
        updateMpesaChannel(index, { is_primary: false })
      })
    }

    addMpesaChannel(newChannel)
    
    // Reset form
    setNewChannel({
      name: "",
      shortcode: "",
      channel_type: "paybill",
      environment: "sandbox",
      consumer_key: "",
      consumer_secret: "",
      passkey: "",
      validation_url: "",
      confirmation_url: "",
      callback_url: "",
      account_mapping: {},
      is_primary: false
    })
    
    setShowAddForm(false)
    toast.success("M-Pesa channel added successfully")
  }

  const handleRemoveChannel = (index: number) => {
    const channel = mpesaChannels[index]
    
    // If removing primary channel, make the first remaining channel primary
    if (channel.is_primary && mpesaChannels.length > 1) {
      const nextPrimaryIndex = index === 0 ? 1 : 0
      updateMpesaChannel(nextPrimaryIndex, { is_primary: true })
    }
    
    removeMpesaChannel(index)
    toast.success("M-Pesa channel removed")
  }

  const handleSetPrimary = (index: number) => {
    // Unset all other primary channels
    mpesaChannels.forEach((_, i) => {
      updateMpesaChannel(i, { is_primary: i === index })
    })
    toast.success("Primary channel updated")
  }

  const toggleCredentialVisibility = (index: number) => {
    setShowCredentials(prev => ({
      ...prev,
      [index]: !prev[index]
    }))
  }

  const renderChannelForm = (
    channel: MpesaChannelData,
    onChange: (field: string, value: any) => void,
    isEditing = false
  ) => (
    <div className="space-y-4">
      {/* Basic Information */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
        <div className="space-y-2">
          <Label htmlFor="name">Channel Name *</Label>
          <Input
            id="name"
            value={channel.name}
            onChange={(e) => onChange("name", e.target.value)}
            placeholder="e.g., Main PayBill, Shop Till"
            className="bg-background/50"
          />
        </div>

        <div className="space-y-2">
          <Label htmlFor="shortcode">Shortcode/Number *</Label>
          <Input
            id="shortcode"
            value={channel.shortcode}
            onChange={(e) => onChange("shortcode", e.target.value)}
            placeholder="e.g., 174379, 123456"
            className="bg-background/50"
          />
        </div>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
        <div className="space-y-2">
          <Label htmlFor="channel_type">Channel Type *</Label>
          <Select
            value={channel.channel_type}
            onValueChange={(value) => onChange("channel_type", value)}
          >
            <SelectTrigger className="bg-background/50">
              <SelectValue />
            </SelectTrigger>
            <SelectContent>
              {CHANNEL_TYPES.map((type) => (
                <SelectItem key={type.value} value={type.value}>
                  <div className="flex items-center gap-2">
                    <span>{type.icon}</span>
                    <div>
                      <div className="font-medium">{type.label}</div>
                      <div className="text-xs text-muted-foreground">{type.description}</div>
                    </div>
                  </div>
                </SelectItem>
              ))}
            </SelectContent>
          </Select>
        </div>

        <div className="space-y-2">
          <Label htmlFor="environment">Environment *</Label>
          <Select
            value={channel.environment}
            onValueChange={(value) => onChange("environment", value)}
          >
            <SelectTrigger className="bg-background/50">
              <SelectValue />
            </SelectTrigger>
            <SelectContent>
              {ENVIRONMENTS.map((env) => (
                <SelectItem key={env.value} value={env.value}>
                  <div className="flex items-center gap-2">
                    <Badge className={env.color} variant="secondary">
                      {env.label}
                    </Badge>
                  </div>
                </SelectItem>
              ))}
            </SelectContent>
          </Select>
        </div>
      </div>

      {/* Credentials */}
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-2 text-base">
            <Shield className="h-4 w-4" />
            Daraja API Credentials
          </CardTitle>
          <CardDescription>
            Get these from your Safaricom Daraja developer account
          </CardDescription>
        </CardHeader>
        <CardContent className="space-y-4">
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            <div className="space-y-2">
              <Label htmlFor="consumer_key">Consumer Key *</Label>
              <Input
                id="consumer_key"
                type="password"
                value={channel.consumer_key}
                onChange={(e) => onChange("consumer_key", e.target.value)}
                placeholder="Your Daraja consumer key"
                className="bg-background/50"
              />
            </div>

            <div className="space-y-2">
              <Label htmlFor="consumer_secret">Consumer Secret *</Label>
              <Input
                id="consumer_secret"
                type="password"
                value={channel.consumer_secret}
                onChange={(e) => onChange("consumer_secret", e.target.value)}
                placeholder="Your Daraja consumer secret"
                className="bg-background/50"
              />
            </div>
          </div>

          {channel.channel_type === "paybill" && (
            <div className="space-y-2">
              <Label htmlFor="passkey">Passkey</Label>
              <Input
                id="passkey"
                type="password"
                value={channel.passkey || ""}
                onChange={(e) => onChange("passkey", e.target.value)}
                placeholder="Your PayBill passkey (if required)"
                className="bg-background/50"
              />
            </div>
          )}
        </CardContent>
      </Card>

      {/* Webhook URLs */}
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-2 text-base">
            <Settings className="h-4 w-4" />
            Webhook URLs (Optional)
          </CardTitle>
          <CardDescription>
            URLs for transaction validation and confirmation
          </CardDescription>
        </CardHeader>
        <CardContent className="space-y-4">
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            <div className="space-y-2">
              <Label htmlFor="validation_url">Validation URL</Label>
              <Input
                id="validation_url"
                type="url"
                value={channel.validation_url || ""}
                onChange={(e) => onChange("validation_url", e.target.value)}
                placeholder="https://yourdomain.com/mpesa/validate"
                className="bg-background/50"
              />
            </div>

            <div className="space-y-2">
              <Label htmlFor="confirmation_url">Confirmation URL</Label>
              <Input
                id="confirmation_url"
                type="url"
                value={channel.confirmation_url || ""}
                onChange={(e) => onChange("confirmation_url", e.target.value)}
                placeholder="https://yourdomain.com/mpesa/confirm"
                className="bg-background/50"
              />
            </div>
          </div>

          <div className="space-y-2">
            <Label htmlFor="callback_url">Callback URL</Label>
            <Input
              id="callback_url"
              type="url"
              value={channel.callback_url || ""}
              onChange={(e) => onChange("callback_url", e.target.value)}
              placeholder="https://yourdomain.com/mpesa/callback"
              className="bg-background/50"
            />
          </div>
        </CardContent>
      </Card>

      {/* Account Mapping for PayBill */}
      {channel.channel_type === "paybill" && (
        <Card>
          <CardHeader>
            <CardTitle className="flex items-center gap-2 text-base">
              <CreditCard className="h-4 w-4" />
              Account Mapping
            </CardTitle>
            <CardDescription>
              Map account references to loyalty programs
            </CardDescription>
          </CardHeader>
          <CardContent>
            <div className="space-y-2">
              <Label htmlFor="account_mapping">Account Mapping (JSON)</Label>
              <Textarea
                id="account_mapping"
                value={JSON.stringify(channel.account_mapping || {}, null, 2)}
                onChange={(e) => {
                  try {
                    const mapping = JSON.parse(e.target.value)
                    onChange("account_mapping", mapping)
                  } catch {
                    // Invalid JSON, ignore
                  }
                }}
                placeholder='{\n  "default": "standard_loyalty",\n  "VIP*": "vip_program",\n  "STUDENT*": "student_program"\n}'
                className="bg-background/50 font-mono text-sm min-h-[100px]"
              />
              <p className="text-xs text-muted-foreground">
                Use * for wildcard matching. Example: "VIP*" matches "VIP001", "VIP999", etc.
              </p>
            </div>
          </CardContent>
        </Card>
      )}

      {/* Primary Channel Toggle */}
      <div className="flex items-center justify-between p-4 bg-muted/50 rounded-lg">
        <div>
          <Label htmlFor="is_primary" className="text-base font-medium">
            Primary Channel
          </Label>
          <p className="text-sm text-muted-foreground">
            The main channel for processing transactions
          </p>
        </div>
        <Switch
          id="is_primary"
          checked={channel.is_primary}
          onCheckedChange={(checked) => onChange("is_primary", checked)}
        />
      </div>
    </div>
  )

  return (
    <div className="space-y-6">
      <div className="text-center mb-6">
        <h3 className="text-xl font-semibold text-foreground mb-2">
          Connect Your M-Pesa Channels
        </h3>
        <p className="text-muted-foreground">
          Add your M-Pesa PayBill, Till, or Buy Goods channels to start collecting payments
        </p>
      </div>

      {/* Existing Channels */}
      {mpesaChannels.length > 0 && (
        <div className="space-y-4">
          <div className="flex items-center justify-between">
            <h4 className="text-lg font-medium">Your M-Pesa Channels</h4>
            <Button
              variant="outline"
              size="sm"
              onClick={() => setShowAddForm(true)}
              className="flex items-center gap-2"
            >
              <Plus className="h-4 w-4" />
              Add Channel
            </Button>
          </div>

          {mpesaChannels.map((channel, index) => (
            <Card key={index} className={channel.is_primary ? "border-primary" : ""}>
              <CardHeader>
                <div className="flex items-center justify-between">
                  <div className="flex items-center gap-3">
                    <div className="text-2xl">
                      {CHANNEL_TYPES.find(t => t.value === channel.channel_type)?.icon}
                    </div>
                    <div>
                      <CardTitle className="flex items-center gap-2">
                        {channel.name}
                        {channel.is_primary && (
                          <Badge variant="default" className="text-xs">
                            Primary
                          </Badge>
                        )}
                      </CardTitle>
                      <CardDescription>
                        {CHANNEL_TYPES.find(t => t.value === channel.channel_type)?.label} • {channel.shortcode}
                      </CardDescription>
                    </div>
                  </div>
                  <div className="flex items-center gap-2">
                    <Badge 
                      className={ENVIRONMENTS.find(e => e.value === channel.environment)?.color}
                      variant="secondary"
                    >
                      {ENVIRONMENTS.find(e => e.value === channel.environment)?.label}
                    </Badge>
                    <Button
                      variant="ghost"
                      size="sm"
                      onClick={() => toggleCredentialVisibility(index)}
                    >
                      {showCredentials[index] ? <EyeOff className="h-4 w-4" /> : <Eye className="h-4 w-4" />}
                    </Button>
                    <Button
                      variant="ghost"
                      size="sm"
                      onClick={() => handleRemoveChannel(index)}
                      className="text-destructive hover:text-destructive"
                    >
                      <Trash2 className="h-4 w-4" />
                    </Button>
                  </div>
                </div>
              </CardHeader>

              {showCredentials[index] && (
                <CardContent>
                  <div className="grid grid-cols-1 md:grid-cols-2 gap-4 text-sm">
                    <div>
                      <Label className="text-xs text-muted-foreground">Consumer Key</Label>
                      <p className="font-mono bg-muted p-2 rounded text-xs break-all">
                        {channel.consumer_key}
                      </p>
                    </div>
                    <div>
                      <Label className="text-xs text-muted-foreground">Consumer Secret</Label>
                      <p className="font-mono bg-muted p-2 rounded text-xs break-all">
                        {channel.consumer_secret}
                      </p>
                    </div>
                  </div>
                  
                  {!channel.is_primary && (
                    <div className="mt-4">
                      <Button
                        variant="outline"
                        size="sm"
                        onClick={() => handleSetPrimary(index)}
                      >
                        Set as Primary
                      </Button>
                    </div>
                  )}
                </CardContent>
              )}
            </Card>
          ))}
        </div>
      )}

      {/* Add New Channel Form */}
      {showAddForm && (
        <Card>
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              <Plus className="h-5 w-5" />
              Add New M-Pesa Channel
            </CardTitle>
            <CardDescription>
              Configure a new M-Pesa payment channel for your business
            </CardDescription>
          </CardHeader>
          <CardContent>
            {renderChannelForm(newChannel, (field, value) => {
              setNewChannel(prev => ({ ...prev, [field]: value }))
            })}

            <Separator className="my-6" />

            <div className="flex items-center justify-end gap-3">
              <Button
                variant="outline"
                onClick={() => setShowAddForm(false)}
              >
                Cancel
              </Button>
              <Button onClick={handleAddChannel}>
                Add Channel
              </Button>
            </div>
          </CardContent>
        </Card>
      )}

      {/* Help Information */}
      <Alert>
        <Info className="h-4 w-4" />
        <AlertDescription>
          <div className="space-y-2">
            <p className="font-medium">Need help setting up M-Pesa?</p>
            <ul className="text-sm space-y-1 ml-4 list-disc">
              <li>Get your Daraja API credentials from the <a href="https://developer.safaricom.co.ke" target="_blank" rel="noopener noreferrer" className="text-primary hover:underline inline-flex items-center gap-1">Safaricom Developer Portal <ExternalLink className="h-3 w-3" /></a></li>
              <li>Use sandbox environment for testing before going live</li>
              <li>PayBill channels support account references for different loyalty programs</li>
              <li>Webhook URLs are optional but recommended for real-time transaction processing</li>
            </ul>
          </div>
        </AlertDescription>
      </Alert>

      {mpesaChannels.length === 0 && !showAddForm && (
        <div className="text-center py-12">
          <CreditCard className="h-12 w-12 text-muted-foreground mx-auto mb-4" />
          <h4 className="text-lg font-medium text-foreground mb-2">No M-Pesa Channels</h4>
          <p className="text-muted-foreground mb-4">
            Add at least one M-Pesa channel to start accepting payments
          </p>
          <Button onClick={() => setShowAddForm(true)} className="flex items-center gap-2">
            <Plus className="h-4 w-4" />
            Add Your First Channel
          </Button>
        </div>
      )}
    </div>
  )
}
