"use client"

import React from "react"
import { useOnboarding } from "@/contexts/onboarding-context"
import { Input } from "@/components/ui/input"
import { Label } from "@/components/ui/label"
import { Textarea } from "@/components/ui/textarea"
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select"
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card"
import { Building, Mail, Phone, Globe, FileText, MapPin } from "lucide-react"

const BUSINESS_TYPES = [
  { value: "retail", label: "Retail Store" },
  { value: "restaurant", label: "Restaurant/Food Service" },
  { value: "service", label: "Service Business" },
  { value: "ecommerce", label: "E-commerce" },
  { value: "healthcare", label: "Healthcare" },
  { value: "education", label: "Education" },
  { value: "automotive", label: "Automotive" },
  { value: "beauty", label: "Beauty & Wellness" },
  { value: "technology", label: "Technology" },
  { value: "finance", label: "Financial Services" },
  { value: "real_estate", label: "Real Estate" },
  { value: "entertainment", label: "Entertainment" },
  { value: "other", label: "Other" }
]

export function BusinessInfoStep() {
  const { data, updateBusinessInfo } = useOnboarding()
  const { businessInfo } = data

  const handleInputChange = (field: string, value: string) => {
    updateBusinessInfo({ [field]: value })
  }

  return (
    <div className="space-y-6">
      <div className="text-center mb-6">
        <h3 className="text-xl font-semibold text-foreground mb-2">
          Tell us about your business
        </h3>
        <p className="text-muted-foreground">
          This information helps us customize your loyalty platform and ensure compliance
        </p>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
        {/* Basic Business Information */}
        <Card>
          <CardHeader>
            <CardTitle className="flex items-center gap-2 text-lg">
              <Building className="h-5 w-5" />
              Basic Information
            </CardTitle>
            <CardDescription>
              Essential details about your business
            </CardDescription>
          </CardHeader>
          <CardContent className="space-y-4">
            <div className="space-y-2">
              <Label htmlFor="businessName">Business Name *</Label>
              <Input
                id="businessName"
                value={businessInfo.businessName}
                onChange={(e) => handleInputChange("businessName", e.target.value)}
                placeholder="e.g., Mama Jane's Electronics"
                className="bg-background/50"
              />
            </div>

            <div className="space-y-2">
              <Label htmlFor="ownerName">Owner/Manager Name *</Label>
              <Input
                id="ownerName"
                value={businessInfo.ownerName}
                onChange={(e) => handleInputChange("ownerName", e.target.value)}
                placeholder="Your full name"
                className="bg-background/50"
              />
            </div>

            <div className="space-y-2">
              <Label htmlFor="businessType">Business Type *</Label>
              <Select
                value={businessInfo.businessType}
                onValueChange={(value) => handleInputChange("businessType", value)}
              >
                <SelectTrigger className="bg-background/50">
                  <SelectValue placeholder="Select your business type" />
                </SelectTrigger>
                <SelectContent>
                  {BUSINESS_TYPES.map((type) => (
                    <SelectItem key={type.value} value={type.value}>
                      {type.label}
                    </SelectItem>
                  ))}
                </SelectContent>
              </Select>
            </div>

            <div className="space-y-2">
              <Label htmlFor="businessDescription">Business Description</Label>
              <Textarea
                id="businessDescription"
                value={businessInfo.businessDescription || ""}
                onChange={(e) => handleInputChange("businessDescription", e.target.value)}
                placeholder="Brief description of your business and what you sell..."
                className="bg-background/50 min-h-[80px]"
              />
            </div>
          </CardContent>
        </Card>

        {/* Contact Information */}
        <Card>
          <CardHeader>
            <CardTitle className="flex items-center gap-2 text-lg">
              <Mail className="h-5 w-5" />
              Contact Information
            </CardTitle>
            <CardDescription>
              How customers and we can reach you
            </CardDescription>
          </CardHeader>
          <CardContent className="space-y-4">
            <div className="space-y-2">
              <Label htmlFor="email">Business Email *</Label>
              <div className="relative">
                <Mail className="absolute left-3 top-3 h-4 w-4 text-muted-foreground" />
                <Input
                  id="email"
                  type="email"
                  value={businessInfo.email}
                  onChange={(e) => handleInputChange("email", e.target.value)}
                  placeholder="business@example.com"
                  className="bg-background/50 pl-10"
                />
              </div>
            </div>

            <div className="space-y-2">
              <Label htmlFor="phone">Business Phone *</Label>
              <div className="relative">
                <Phone className="absolute left-3 top-3 h-4 w-4 text-muted-foreground" />
                <Input
                  id="phone"
                  type="tel"
                  value={businessInfo.phone}
                  onChange={(e) => handleInputChange("phone", e.target.value)}
                  placeholder="254712345678"
                  className="bg-background/50 pl-10"
                />
              </div>
              <p className="text-xs text-muted-foreground">
                Format: 254XXXXXXXXX (Kenyan mobile number)
              </p>
            </div>

            <div className="space-y-2">
              <Label htmlFor="website">Website (Optional)</Label>
              <div className="relative">
                <Globe className="absolute left-3 top-3 h-4 w-4 text-muted-foreground" />
                <Input
                  id="website"
                  type="url"
                  value={businessInfo.website || ""}
                  onChange={(e) => handleInputChange("website", e.target.value)}
                  placeholder="https://www.yourbusiness.com"
                  className="bg-background/50 pl-10"
                />
              </div>
            </div>

            <div className="space-y-2">
              <Label htmlFor="businessAddress">Business Address</Label>
              <div className="relative">
                <MapPin className="absolute left-3 top-3 h-4 w-4 text-muted-foreground" />
                <Textarea
                  id="businessAddress"
                  value={businessInfo.businessAddress || ""}
                  onChange={(e) => handleInputChange("businessAddress", e.target.value)}
                  placeholder="Street address, city, county..."
                  className="bg-background/50 pl-10 min-h-[60px]"
                />
              </div>
            </div>
          </CardContent>
        </Card>
      </div>

      {/* Additional Information */}
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-2 text-lg">
            <FileText className="h-5 w-5" />
            Additional Information
          </CardTitle>
          <CardDescription>
            Optional details for compliance and better service
          </CardDescription>
        </CardHeader>
        <CardContent>
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            <div className="space-y-2">
              <Label htmlFor="taxId">Tax ID/PIN (Optional)</Label>
              <Input
                id="taxId"
                value={businessInfo.taxId || ""}
                onChange={(e) => handleInputChange("taxId", e.target.value)}
                placeholder="KRA PIN or Tax ID"
                className="bg-background/50"
              />
              <p className="text-xs text-muted-foreground">
                Required for businesses with annual revenue above KES 5M
              </p>
            </div>
          </div>
        </CardContent>
      </Card>

      {/* Information Notice */}
      <div className="bg-blue-50 dark:bg-blue-950/20 border border-blue-200 dark:border-blue-800 rounded-lg p-4">
        <div className="flex items-start gap-3">
          <div className="w-5 h-5 rounded-full bg-blue-500 flex items-center justify-center flex-shrink-0 mt-0.5">
            <span className="text-white text-xs font-bold">i</span>
          </div>
          <div className="text-sm">
            <p className="font-medium text-blue-900 dark:text-blue-100 mb-1">
              Data Privacy & Security
            </p>
            <p className="text-blue-700 dark:text-blue-200">
              Your business information is encrypted and stored securely. We comply with Kenya's Data Protection Act 
              and only use this information to provide and improve our services. You can update or delete this 
              information at any time from your dashboard.
            </p>
          </div>
        </div>
      </div>
    </div>
  )
}
