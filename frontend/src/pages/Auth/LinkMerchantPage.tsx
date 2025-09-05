"use client";

import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '../../components/ui/card';
import { Label } from '../../components/ui/label';
import { Input } from '../../components/ui/input';
import { Button } from '../../components/ui/button';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '../../components/ui/select';
import { useAuth } from '../../context/AuthContext';
import api from '../../lib/api';
import { MerchantLinkRequest, MerchantResponse } from '../../types/api';
import { BusinessType } from '../../types/enums';
import { toast } from 'react-hot-toast';

const LinkMerchantPage = () => {
  const [businessName, setBusinessName] = useState('');
  const [ownerName, setOwnerName] = useState('');
  const [email, setEmail] = useState('');
  const [phone, setPhone] = useState('');
  const [businessType, setBusinessType] = useState<BusinessType>(BusinessType.RETAIL);
  const [mpesaTillNumber, setMpesaTillNumber] = useState('');
  const [loading, setLoading] = useState(false);
  const navigate = useNavigate();
  const { user, checkAuth } = useAuth();

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setLoading(true);
    try {
      const merchantData: MerchantLinkRequest = {
        business_name: businessName,
        owner_name: ownerName,
        email,
        phone,
        business_type: businessType,
        mpesa_till_number: mpesaTillNumber,
      };
      const response = await api.post<MerchantResponse>('/api/v1/merchants/link-user-merchant', merchantData);
      toast.success('Merchant created and linked successfully!');
      await checkAuth(); // Re-fetch user to update merchant_id in context
      navigate('/dashboard');
    } catch (error: any) {
      console.error('Failed to link merchant:', error);
      toast.error(error.response?.data?.detail || 'Failed to link merchant. Please try again.');
    } finally {
      setLoading(false);
    }
  };

  // If user already has a merchant_id, redirect them
  if (user && user.merchant_id) {
    navigate('/dashboard');
    return null;
  }

  return (
    <div className="flex items-center justify-center min-h-[calc(100vh-4rem)]">
      <Card className="w-full max-w-lg">
        <CardHeader className="space-y-1">
          <CardTitle className="text-2xl">Link Your Business</CardTitle>
          <CardDescription>
            Create a new merchant profile for your business.
          </CardDescription>
        </CardHeader>
        <CardContent>
          <form onSubmit={handleSubmit} className="grid gap-4">
            <div className="grid gap-2">
              <Label htmlFor="businessName">Business Name</Label>
              <Input
                id="businessName"
                type="text"
                placeholder="My Awesome Shop"
                value={businessName}
                onChange={(e) => setBusinessName(e.target.value)}
                required
              />
            </div>
            <div className="grid gap-2">
              <Label htmlFor="ownerName">Owner Name</Label>
              <Input
                id="ownerName"
                type="text"
                placeholder="Jane Doe"
                value={ownerName}
                onChange={(e) => setOwnerName(e.target.value)}
                required
              />
            </div>
            <div className="grid gap-2">
              <Label htmlFor="email">Business Email</Label>
              <Input
                id="email"
                type="email"
                placeholder="business@example.com"
                value={email}
                onChange={(e) => setEmail(e.target.value)}
                required
              />
            </div>
            <div className="grid gap-2">
              <Label htmlFor="phone">Business Phone</Label>
              <Input
                id="phone"
                type="tel"
                placeholder="2547XXXXXXXX"
                value={phone}
                onChange={(e) => setPhone(e.target.value)}
                required
              />
            </div>
            <div className="grid gap-2">
              <Label htmlFor="businessType">Business Type</Label>
              <Select value={businessType} onValueChange={(value: BusinessType) => setBusinessType(value)}>
                <SelectTrigger id="businessType">
                  <SelectValue placeholder="Select business type" />
                </SelectTrigger>
                <SelectContent>
                  {Object.values(BusinessType).map((type) => (
                    <SelectItem key={type} value={type}>
                      {type.charAt(0).toUpperCase() + type.slice(1)}
                    </SelectItem>
                  ))}
                </SelectContent>
              </Select>
            </div>
            <div className="grid gap-2">
              <Label htmlFor="mpesaTillNumber">M-Pesa Till Number</Label>
              <Input
                id="mpesaTillNumber"
                type="text"
                placeholder="e.g., 123456"
                value={mpesaTillNumber}
                onChange={(e) => setMpesaTillNumber(e.target.value)}
                required
              />
            </div>
            <Button type="submit" className="w-full" disabled={loading}>
              {loading ? 'Linking Business...' : 'Link Business'}
            </Button>
          </form>
        </CardContent>
      </Card>
    </div>
  );
};

export default LinkMerchantPage;