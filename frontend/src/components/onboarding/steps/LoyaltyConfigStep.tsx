"use client"

import React, { useState } from "react"
import { useOnboarding } from "@/contexts/onboarding-context"
import { Input } from "@/components/ui/input"
import { Label } from "@/components/ui/label"
import { Textarea } from "@/components/ui/textarea"
import { Switch } from "@/components/ui/switch"
import { Button } from "@/components/ui/button"
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card"
import { Badge } from "@/components/ui/badge"
import { Separator } from "@/components/ui/separator"
import { 
  Gift, 
  Star, 
  Users, 
  TrendingUp, 
  Plus, 
  Trash2, 
  Edit3,
  Crown,
  Award,
  Zap,
  Heart
} from "lucide-react"

const TIER_COLORS = [
  "bg-amber-100 text-amber-800 dark:bg-amber-900/20 dark:text-amber-400", // Bronze
  "bg-gray-100 text-gray-800 dark:bg-gray-900/20 dark:text-gray-400",     // Silver
  "bg-yellow-100 text-yellow-800 dark:bg-yellow-900/20 dark:text-yellow-400", // Gold
  "bg-purple-100 text-purple-800 dark:bg-purple-900/20 dark:text-purple-400"  // Platinum
]

const TIER_ICONS = [Crown, Award, Star, Zap]

export function LoyaltyConfigStep() {
  const { data, updateLoyaltyProgram } = useOnboarding()
  const { loyaltyProgram } = data
  
  const [editingTier, setEditingTier] = useState<number | null>(null)

  const handleProgramChange = (field: string, value: any) => {
    updateLoyaltyProgram({ [field]: value })
  }

  const handleTierChange = (index: number, field: string, value: any) => {
    const updatedTiers = [...(loyaltyProgram.tiers || [])]
    updatedTiers[index] = { ...updatedTiers[index], [field]: value }
    updateLoyaltyProgram({ tiers: updatedTiers })
  }

  const addTier = () => {
    const newTier = {
      name: `Tier ${(loyaltyProgram.tiers?.length || 0) + 1}`,
      min_points: (loyaltyProgram.tiers?.length || 0) * 1000,
      multiplier: 1 + (loyaltyProgram.tiers?.length || 0) * 0.2,
      benefits: ["Standard rewards"]
    }
    
    const updatedTiers = [...(loyaltyProgram.tiers || []), newTier]
    updateLoyaltyProgram({ tiers: updatedTiers })
  }

  const removeTier = (index: number) => {
    const updatedTiers = loyaltyProgram.tiers?.filter((_, i) => i !== index) || []
    updateLoyaltyProgram({ tiers: updatedTiers })
  }

  const addBenefit = (tierIndex: number) => {
    const updatedTiers = [...(loyaltyProgram.tiers || [])]
    updatedTiers[tierIndex].benefits.push("")
    updateLoyaltyProgram({ tiers: updatedTiers })
  }

  const updateBenefit = (tierIndex: number, benefitIndex: number, value: string) => {
    const updatedTiers = [...(loyaltyProgram.tiers || [])]
    updatedTiers[tierIndex].benefits[benefitIndex] = value
    updateLoyaltyProgram({ tiers: updatedTiers })
  }

  const removeBenefit = (tierIndex: number, benefitIndex: number) => {
    const updatedTiers = [...(loyaltyProgram.tiers || [])]
    updatedTiers[tierIndex].benefits = updatedTiers[tierIndex].benefits.filter((_, i) => i !== benefitIndex)
    updateLoyaltyProgram({ tiers: updatedTiers })
  }

  return (
    <div className="space-y-6">
      <div className="text-center mb-6">
        <h3 className="text-xl font-semibold text-foreground mb-2">
          Configure Your Loyalty Program
        </h3>
        <p className="text-muted-foreground">
          Design a loyalty program that keeps customers coming back
        </p>
      </div>

      {/* Basic Program Settings */}
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <Gift className="h-5 w-5" />
            Program Details
          </CardTitle>
          <CardDescription>
            Basic information about your loyalty program
          </CardDescription>
        </CardHeader>
        <CardContent className="space-y-4">
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            <div className="space-y-2">
              <Label htmlFor="program_name">Program Name *</Label>
              <Input
                id="program_name"
                value={loyaltyProgram.name}
                onChange={(e) => handleProgramChange("name", e.target.value)}
                placeholder="e.g., VIP Rewards, Customer Club"
                className="bg-background/50"
              />
            </div>

            <div className="space-y-2">
              <Label htmlFor="points_per_shilling">Points per KES *</Label>
              <Input
                id="points_per_shilling"
                type="number"
                min="0.1"
                step="0.1"
                value={loyaltyProgram.points_per_shilling}
                onChange={(e) => handleProgramChange("points_per_shilling", parseFloat(e.target.value) || 1)}
                className="bg-background/50"
              />
              <p className="text-xs text-muted-foreground">
                How many points customers earn per KES spent
              </p>
            </div>
          </div>

          <div className="space-y-2">
            <Label htmlFor="program_description">Program Description *</Label>
            <Textarea
              id="program_description"
              value={loyaltyProgram.description}
              onChange={(e) => handleProgramChange("description", e.target.value)}
              placeholder="Describe your loyalty program benefits and how it works..."
              className="bg-background/50 min-h-[80px]"
            />
          </div>

          <div className="space-y-2">
            <Label htmlFor="redemption_rate">Redemption Rate (Points per KES) *</Label>
            <Input
              id="redemption_rate"
              type="number"
              min="1"
              value={loyaltyProgram.redemption_rate}
              onChange={(e) => handleProgramChange("redemption_rate", parseInt(e.target.value) || 100)}
              className="bg-background/50"
            />
            <p className="text-xs text-muted-foreground">
              How many points equal 1 KES when redeeming rewards
            </p>
          </div>
        </CardContent>
      </Card>

      {/* Bonus Settings */}
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <TrendingUp className="h-5 w-5" />
            Bonus Points
          </CardTitle>
          <CardDescription>
            Special bonuses to encourage engagement
          </CardDescription>
        </CardHeader>
        <CardContent>
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
            <div className="space-y-2">
              <Label htmlFor="welcome_bonus" className="flex items-center gap-2">
                <Heart className="h-4 w-4" />
                Welcome Bonus
              </Label>
              <Input
                id="welcome_bonus"
                type="number"
                min="0"
                value={loyaltyProgram.welcome_bonus}
                onChange={(e) => handleProgramChange("welcome_bonus", parseInt(e.target.value) || 0)}
                className="bg-background/50"
              />
              <p className="text-xs text-muted-foreground">
                Points for new customers
              </p>
            </div>

            <div className="space-y-2">
              <Label htmlFor="referral_bonus" className="flex items-center gap-2">
                <Users className="h-4 w-4" />
                Referral Bonus
              </Label>
              <Input
                id="referral_bonus"
                type="number"
                min="0"
                value={loyaltyProgram.referral_bonus}
                onChange={(e) => handleProgramChange("referral_bonus", parseInt(e.target.value) || 0)}
                className="bg-background/50"
              />
              <p className="text-xs text-muted-foreground">
                Points for successful referrals
              </p>
            </div>

            <div className="space-y-2">
              <Label htmlFor="birthday_bonus" className="flex items-center gap-2">
                <Gift className="h-4 w-4" />
                Birthday Bonus
              </Label>
              <Input
                id="birthday_bonus"
                type="number"
                min="0"
                value={loyaltyProgram.birthday_bonus}
                onChange={(e) => handleProgramChange("birthday_bonus", parseInt(e.target.value) || 0)}
                className="bg-background/50"
              />
              <p className="text-xs text-muted-foreground">
                Annual birthday points
              </p>
            </div>
          </div>
        </CardContent>
      </Card>

      {/* Tier System */}
      <Card>
        <CardHeader>
          <div className="flex items-center justify-between">
            <div>
              <CardTitle className="flex items-center gap-2">
                <Star className="h-5 w-5" />
                Tier System
              </CardTitle>
              <CardDescription>
                Create tiers to reward your most loyal customers
              </CardDescription>
            </div>
            <Switch
              checked={loyaltyProgram.tier_system_enabled}
              onCheckedChange={(checked) => handleProgramChange("tier_system_enabled", checked)}
            />
          </div>
        </CardHeader>

        {loyaltyProgram.tier_system_enabled && (
          <CardContent className="space-y-4">
            <div className="flex items-center justify-between">
              <p className="text-sm text-muted-foreground">
                Design tiers that provide increasing benefits as customers spend more
              </p>
              <Button
                variant="outline"
                size="sm"
                onClick={addTier}
                className="flex items-center gap-2"
              >
                <Plus className="h-4 w-4" />
                Add Tier
              </Button>
            </div>

            <div className="space-y-4">
              {loyaltyProgram.tiers?.map((tier, index) => {
                const TierIcon = TIER_ICONS[index % TIER_ICONS.length]
                const tierColor = TIER_COLORS[index % TIER_COLORS.length]
                
                return (
                  <Card key={index} className="border-l-4 border-l-primary">
                    <CardHeader>
                      <div className="flex items-center justify-between">
                        <div className="flex items-center gap-3">
                          <TierIcon className="h-5 w-5 text-primary" />
                          <div>
                            <CardTitle className="text-base flex items-center gap-2">
                              {editingTier === index ? (
                                <Input
                                  value={tier.name}
                                  onChange={(e) => handleTierChange(index, "name", e.target.value)}
                                  className="w-32 h-8"
                                  onBlur={() => setEditingTier(null)}
                                  onKeyDown={(e) => e.key === "Enter" && setEditingTier(null)}
                                  autoFocus
                                />
                              ) : (
                                <>
                                  {tier.name}
                                  <Button
                                    variant="ghost"
                                    size="sm"
                                    onClick={() => setEditingTier(index)}
                                    className="h-6 w-6 p-0"
                                  >
                                    <Edit3 className="h-3 w-3" />
                                  </Button>
                                </>
                              )}
                              <Badge className={tierColor} variant="secondary">
                                Tier {index + 1}
                              </Badge>
                            </CardTitle>
                            <CardDescription>
                              {tier.min_points.toLocaleString()} points minimum • {tier.multiplier}x multiplier
                            </CardDescription>
                          </div>
                        </div>
                        <Button
                          variant="ghost"
                          size="sm"
                          onClick={() => removeTier(index)}
                          className="text-destructive hover:text-destructive"
                        >
                          <Trash2 className="h-4 w-4" />
                        </Button>
                      </div>
                    </CardHeader>
                    <CardContent className="space-y-4">
                      <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                        <div className="space-y-2">
                          <Label htmlFor={`tier_${index}_min_points`}>Minimum Points</Label>
                          <Input
                            id={`tier_${index}_min_points`}
                            type="number"
                            min="0"
                            value={tier.min_points}
                            onChange={(e) => handleTierChange(index, "min_points", parseInt(e.target.value) || 0)}
                            className="bg-background/50"
                          />
                        </div>
                        <div className="space-y-2">
                          <Label htmlFor={`tier_${index}_multiplier`}>Points Multiplier</Label>
                          <Input
                            id={`tier_${index}_multiplier`}
                            type="number"
                            min="1"
                            step="0.1"
                            value={tier.multiplier}
                            onChange={(e) => handleTierChange(index, "multiplier", parseFloat(e.target.value) || 1)}
                            className="bg-background/50"
                          />
                        </div>
                      </div>

                      <div className="space-y-2">
                        <div className="flex items-center justify-between">
                          <Label>Benefits</Label>
                          <Button
                            variant="outline"
                            size="sm"
                            onClick={() => addBenefit(index)}
                            className="flex items-center gap-1 text-xs"
                          >
                            <Plus className="h-3 w-3" />
                            Add Benefit
                          </Button>
                        </div>
                        <div className="space-y-2">
                          {tier.benefits.map((benefit, benefitIndex) => (
                            <div key={benefitIndex} className="flex items-center gap-2">
                              <Input
                                value={benefit}
                                onChange={(e) => updateBenefit(index, benefitIndex, e.target.value)}
                                placeholder="e.g., Priority support, Exclusive offers"
                                className="bg-background/50"
                              />
                              <Button
                                variant="ghost"
                                size="sm"
                                onClick={() => removeBenefit(index, benefitIndex)}
                                className="text-destructive hover:text-destructive flex-shrink-0"
                              >
                                <Trash2 className="h-4 w-4" />
                              </Button>
                            </div>
                          ))}
                        </div>
                      </div>
                    </CardContent>
                  </Card>
                )
              })}
            </div>

            {(!loyaltyProgram.tiers || loyaltyProgram.tiers.length === 0) && (
              <div className="text-center py-8 border-2 border-dashed border-muted-foreground/25 rounded-lg">
                <Star className="h-8 w-8 text-muted-foreground mx-auto mb-2" />
                <p className="text-muted-foreground">No tiers created yet</p>
                <Button
                  variant="outline"
                  onClick={addTier}
                  className="mt-2 flex items-center gap-2"
                >
                  <Plus className="h-4 w-4" />
                  Create Your First Tier
                </Button>
              </div>
            )}
          </CardContent>
        )}
      </Card>

      {/* Program Preview */}
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <Award className="h-5 w-5" />
            Program Preview
          </CardTitle>
          <CardDescription>
            How your loyalty program will look to customers
          </CardDescription>
        </CardHeader>
        <CardContent>
          <div className="bg-gradient-to-br from-primary/5 to-primary/10 rounded-lg p-6 space-y-4">
            <div className="text-center">
              <h4 className="text-lg font-semibold text-foreground">{loyaltyProgram.name}</h4>
              <p className="text-sm text-muted-foreground mt-1">{loyaltyProgram.description}</p>
            </div>

            <Separator />

            <div className="grid grid-cols-1 md:grid-cols-3 gap-4 text-center">
              <div className="bg-background/50 rounded-lg p-3">
                <div className="text-2xl font-bold text-primary">{loyaltyProgram.points_per_shilling}</div>
                <div className="text-xs text-muted-foreground">Points per KES</div>
              </div>
              <div className="bg-background/50 rounded-lg p-3">
                <div className="text-2xl font-bold text-primary">{loyaltyProgram.redemption_rate}</div>
                <div className="text-xs text-muted-foreground">Points = 1 KES</div>
              </div>
              <div className="bg-background/50 rounded-lg p-3">
                <div className="text-2xl font-bold text-primary">{loyaltyProgram.welcome_bonus}</div>
                <div className="text-xs text-muted-foreground">Welcome Bonus</div>
              </div>
            </div>

            {loyaltyProgram.tier_system_enabled && loyaltyProgram.tiers && loyaltyProgram.tiers.length > 0 && (
              <>
                <Separator />
                <div>
                  <h5 className="font-medium text-foreground mb-3 text-center">Membership Tiers</h5>
                  <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-3">
                    {loyaltyProgram.tiers.map((tier, index) => {
                      const TierIcon = TIER_ICONS[index % TIER_ICONS.length]
                      const tierColor = TIER_COLORS[index % TIER_COLORS.length]
                      
                      return (
                        <div key={index} className="bg-background/50 rounded-lg p-3 text-center">
                          <TierIcon className="h-6 w-6 mx-auto mb-2 text-primary" />
                          <div className="font-medium text-sm">{tier.name}</div>
                          <Badge className={`${tierColor} text-xs mt-1`} variant="secondary">
                            {tier.multiplier}x Points
                          </Badge>
                          <div className="text-xs text-muted-foreground mt-1">
                            {tier.min_points.toLocaleString()}+ pts
                          </div>
                        </div>
                      )
                    })}
                  </div>
                </div>
              </>
            )}
          </div>
        </CardContent>
      </Card>
    </div>
  )
}
