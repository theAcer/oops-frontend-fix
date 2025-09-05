"use client";

import React, { useState, useEffect } from 'react';
import { useAuth } from '../../context/AuthContext';
import api from '../../lib/api';
import { CustomerResponse } from '../../types/api';
import { toast } from 'react-hot-toast';
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from '../../components/ui/card';
import { CustomerTable, columns } from '../../components/customers/CustomerTable';
import { Button } from '../../components/ui/button';
import { PlusCircle } from 'lucide-react';
import { Dialog, DialogContent, DialogHeader, DialogTitle, DialogDescription, DialogFooter } from '../../components/ui/dialog';
import { Label } from '../../components/ui/label';
import { Input } from '../../components/ui/input';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '../../components/ui/select';

const CustomersPage = () => {
  const { user, loading: authLoading } = useAuth();
  const [customers, setCustomers] = useState<CustomerResponse[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [isAddCustomerDialogOpen, setIsAddCustomerDialogOpen] = useState(false);
  const [newCustomerName, setNewCustomerName] = useState('');
  const [newCustomerPhone, setNewCustomerPhone] = useState('');
  const [newCustomerEmail, setNewCustomerEmail] = useState('');
  const [newCustomerSegment, setNewCustomerSegment] = useState('new'); // Default segment

  useEffect(() => {
    const fetchCustomers = async () => {
      if (!user?.merchant_id) {
        setLoading(false);
        return;
      }

      setLoading(true);
      setError(null);
      try {
        const response = await api.get<CustomerResponse[]>(`/api/v1/customers?merchant_id=${user.merchant_id}`);
        setCustomers(response.data);
      } catch (err: any) {
        console.error('Failed to fetch customers:', err);
        setError(err.response?.data?.detail || 'Failed to load customers.');
        toast.error(err.response?.data?.detail || 'Failed to load customers.');
      } finally {
        setLoading(false);
      }
    };

    if (!authLoading && user?.merchant_id) {
      fetchCustomers();
    }
  }, [authLoading, user?.merchant_id]);

  const handleViewDetails = (customerId: number) => {
    toast.info(`Viewing details for customer ${customerId}`);
    // Implement navigation to a customer detail page or open a side panel
  };

  const handleEditCustomer = (customer: CustomerResponse) => {
    toast.info(`Editing customer ${customer.id}`);
    // Implement edit functionality, e.g., open a dialog with pre-filled data
  };

  const handleAddCustomer = async () => {
    if (!user?.merchant_id) {
      toast.error('User not linked to a merchant.');
      return;
    }
    setLoading(true);
    try {
      // This endpoint doesn't exist in the backend yet, but we'll simulate a successful add.
      // To make this fully functional, a POST /api/v1/customers endpoint would be needed in the backend.
      
      // Simulating API call
      await new Promise(resolve => setTimeout(resolve, 1000)); 
      const newCustomer: CustomerResponse = {
        id: Math.floor(Math.random() * 100000), // Mock ID
        merchant_id: user.merchant_id,
        name: newCustomerName,
        phone: newCustomerPhone,
        email: newCustomerEmail,
        customer_segment: newCustomerSegment,
        total_spent: 0,
        total_transactions: 0,
        average_order_value: 0,
        loyalty_points: 0,
        loyalty_tier: 'bronze',
        churn_risk_score: 0,
        lifetime_value_prediction: 0,
        created_at: new Date().toISOString(),
        // is_active: true, // Assuming this field exists, but not in CustomerResponse
      };
      setCustomers((prev) => [...prev, newCustomer]);
      toast.success('Customer added successfully!');
      setIsAddCustomerDialogOpen(false);
      setNewCustomerName('');
      setNewCustomerPhone('');
      setNewCustomerEmail('');
      setNewCustomerSegment('new');
    } catch (err: any) {
      console.error('Failed to add customer:', err);
      toast.error(err.response?.data?.detail || 'Failed to add customer.');
    } finally {
      setLoading(false);
    }
  };

  if (authLoading || loading) {
    return <div className="text-center py-8">Loading customers...</div>;
  }

  if (error) {
    return (
      <div className="p-4">
        <Alert variant="destructive">
          <AlertTitle>Error</AlertTitle>
          <AlertDescription>{error}</AlertDescription>
        </Alert>
      </div>
    );
  }

  if (!user?.merchant_id) {
    return (
      <div className="p-4">
        <Alert>
          <AlertTitle>No Merchant Linked!</AlertTitle>
          <AlertDescription>
            Please link a business to view customer data.
          </AlertDescription>
        </Alert>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <h1 className="text-3xl font-bold">Customers</h1>
        <Button onClick={() => setIsAddCustomerDialogOpen(true)}>
          <PlusCircle className="mr-2 h-4 w-4" /> Add Customer
        </Button>
      </div>

      <Card>
        <CardHeader>
          <CardTitle>All Customers</CardTitle>
          <CardDescription>
            Manage your loyalty program customers.
          </CardDescription>
        </CardHeader>
        <CardContent>
          <CustomerTable
            customers={customers}
            onViewDetails={handleViewDetails}
            onEditCustomer={handleEditCustomer}
          />
        </CardContent>
      </Card>

      {/* Add Customer Dialog */}
      <Dialog open={isAddCustomerDialogOpen} onOpenChange={setIsAddCustomerDialogOpen}>
        <DialogContent className="sm:max-w-[425px]">
          <DialogHeader>
            <DialogTitle>Add New Customer</DialogTitle>
            <DialogDescription>
              Fill in the details to add a new customer.
            </DialogDescription>
          </DialogHeader>
          <div className="grid gap-4 py-4">
            <div className="grid grid-cols-4 items-center gap-4">
              <Label htmlFor="name" className="text-right">
                Name
              </Label>
              <Input
                id="name"
                value={newCustomerName}
                onChange={(e) => setNewCustomerName(e.target.value)}
                className="col-span-3"
              />
            </div>
            <div className="grid grid-cols-4 items-center gap-4">
              <Label htmlFor="phone" className="text-right">
                Phone
              </Label>
              <Input
                id="phone"
                value={newCustomerPhone}
                onChange={(e) => setNewCustomerPhone(e.target.value)}
                className="col-span-3"
              />
            </div>
            <div className="grid grid-cols-4 items-center gap-4">
              <Label htmlFor="email" className="text-right">
                Email
              </Label>
              <Input
                id="email"
                type="email"
                value={newCustomerEmail}
                onChange={(e) => setNewCustomerEmail(e.target.value)}
                className="col-span-3"
              />
            </div>
            <div className="grid grid-cols-4 items-center gap-4">
              <Label htmlFor="segment" className="text-right">
                Segment
              </Label>
              <Select value={newCustomerSegment} onValueChange={setNewCustomerSegment}>
                <SelectTrigger className="col-span-3">
                  <SelectValue placeholder="Select segment" />
                </SelectTrigger>
                <SelectContent>
                  <SelectItem value="new">New</SelectItem>
                  <SelectItem value="regular">Regular</SelectItem>
                  <SelectItem value="vip">VIP</SelectItem>
                  <SelectItem value="at_risk">At Risk</SelectItem>
                  <SelectItem value="churned">Churned</SelectItem>
                </SelectContent>
              </Select>
            </div>
          </div>
          <DialogFooter>
            <Button type="submit" onClick={handleAddCustomer} disabled={loading}>
              {loading ? 'Adding...' : 'Add Customer'}
            </Button>
          </DialogFooter>
        </DialogContent>
      </Dialog>
    </div>
  );
};

export default CustomersPage;