"use client";

import React, { useState, useEffect } from 'react';
import { useAuth } from '../../context/AuthContext';
import api from '../../lib/api';
import { TransactionResponse, SimulateDarajaTransactionRequest } from '../../types/api';
import { toast } from 'react-hot-toast';
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from '../../components/ui/card';
import { Alert, AlertDescription, AlertTitle } from '../../components/ui/alert';
import { Terminal, RefreshCw, Download, PlusCircle } from 'lucide-react';
import { DataTable } from '../../components/ui/data-table';
import { ColumnDef } from '@tanstack/react-table';
import { Badge } from '../../components/ui/badge';
import { format } from 'date-fns';
import { Button } from '../../components/ui/button';
import { Dialog, DialogContent, DialogHeader, DialogTitle, DialogDescription, DialogFooter } from '../../components/ui/dialog';
import { Label } from '../../components/ui/label';
import { Input } from '../../components/ui/input';

// Define columns for the data table
const columns: ColumnDef<TransactionResponse>[] = [
  {
    accessorKey: 'transaction_date',
    header: 'Date',
    cell: ({ row }) => format(new Date(row.getValue('transaction_date')), 'MMM dd, yyyy HH:mm'),
  },
  {
    accessorKey: 'mpesa_receipt_number',
    header: 'Receipt No.',
  },
  {
    accessorKey: 'customer_name',
    header: 'Customer Name',
    cell: ({ row }) => row.original.customer_name || row.original.customer_phone,
  },
  {
    accessorKey: 'amount',
    header: 'Amount (Ksh)',
    cell: ({ row }) => <div className="text-right">{row.getValue('amount').toLocaleString('en-KE', { minimumFractionDigits: 2, maximumFractionDigits: 2 })}</div>,
  },
  {
    accessorKey: 'status',
    header: 'Status',
    cell: ({ row }) => {
      const status: string = row.getValue('status');
      const getStatusColor = (status: string) => {
        switch (status.toLowerCase()) {
          case 'completed':
            return 'bg-green-100 text-green-800';
          case 'failed':
            return 'bg-red-100 text-red-800';
          case 'pending':
            return 'bg-yellow-100 text-yellow-800';
          default:
            return 'bg-gray-100 text-gray-800';
        }
      };
      return <Badge className={getStatusColor(status)}>{status.charAt(0).toUpperCase() + status.slice(1)}</Badge>;
    },
  },
  {
    accessorKey: 'loyalty_points_earned',
    header: 'Points Earned',
    cell: ({ row }) => <div className="text-right">{row.getValue('loyalty_points_earned')}</div>,
  },
];

const TransactionsPage = () => {
  const { user, loading: authLoading } = useAuth();
  const [transactions, setTransactions] = useState<TransactionResponse[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [syncing, setSyncing] = useState(false);
  const [isSimulateDialogOpen, setIsSimulateDialogOpen] = useState(false);
  const [simulateData, setSimulateData] = useState<SimulateDarajaTransactionRequest>({
    till_number: '',
    amount: 0,
    customer_phone: '',
    customer_name: '',
  });
  const [simulating, setSimulating] = useState(false);

  const fetchTransactions = async () => {
    if (!user?.merchant_id) {
      setLoading(false);
      return;
    }

    setLoading(true);
    setError(null);
    try {
      const response = await api.get<{ transactions: TransactionResponse[]; total: number }>(
        `/api/v1/transactions?merchant_id=${user.merchant_id}`
      );
      setTransactions(response.data.transactions);
    } catch (err: any) {
      console.error('Failed to fetch transactions:', err);
      setError(err.response?.data?.detail || 'Failed to load transactions.');
      toast.error(err.response?.data?.detail || 'Failed to load transactions.');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    if (!authLoading && user?.merchant_id) {
      fetchTransactions();
      setSimulateData((prev) => ({ ...prev, till_number: user.mpesa_till_number || '' }));
    }
  }, [authLoading, user?.merchant_id, user?.mpesa_till_number]);

  const handleSyncTransactions = async () => {
    if (!user?.merchant_id) {
      toast.error('User not linked to a merchant.');
      return;
    }
    setSyncing(true);
    try {
      await api.post(`/api/v1/transactions/sync-daraja`, { merchant_id: user.merchant_id });
      toast.success('Transactions synced successfully!');
      fetchTransactions(); // Refresh data
    } catch (err: any) {
      console.error('Failed to sync transactions:', err);
      toast.error(err.response?.data?.detail || 'Failed to sync transactions.');
    } finally {
      setSyncing(false);
    }
  };

  const handleSimulateTransaction = async () => {
    if (!user?.merchant_id) {
      toast.error('User not linked to a merchant.');
      return;
    }
    setSimulating(true);
    try {
      await api.post('/api/v1/webhooks/daraja/simulate-transaction', simulateData);
      toast.success('Simulated transaction processed!');
      setIsSimulateDialogOpen(false);
      fetchTransactions(); // Refresh data
    } catch (err: any) {
      console.error('Failed to simulate transaction:', err);
      toast.error(err.response?.data?.detail || 'Failed to simulate transaction.');
    } finally {
      setSimulating(false);
    }
  };

  if (authLoading || loading) {
    return <div className="text-center py-8">Loading transactions...</div>;
  }

  if (error) {
    return (
      <div className="p-4">
        <Alert variant="destructive">
          <Terminal className="h-4 w-4" />
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
          <Terminal className="h-4 w-4" />
          <AlertTitle>No Merchant Linked!</AlertTitle>
          <AlertDescription>
            Please link a business to view transaction data.
          </AlertDescription>
        </Alert>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <h1 className="text-3xl font-bold">Transactions</h1>
        <div className="flex space-x-2">
          <Button onClick={() => setIsSimulateDialogOpen(true)} variant="outline">
            <PlusCircle className="mr-2 h-4 w-4" /> Simulate M-Pesa
          </Button>
          <Button onClick={handleSyncTransactions} disabled={syncing}>
            <RefreshCw className={`mr-2 h-4 w-4 ${syncing ? 'animate-spin' : ''}`} /> Sync from Daraja
          </Button>
          <Button variant="outline">
            <Download className="mr-2 h-4 w-4" /> Export
          </Button>
        </div>
      </div>

      <Card>
        <CardHeader>
          <CardTitle>Transaction History</CardTitle>
          <CardDescription>
            All transactions processed through your business.
          </CardDescription>
        </CardHeader>
        <CardContent>
          <DataTable columns={columns} data={transactions} />
        </CardContent>
      </Card>

      {/* Simulate Transaction Dialog */}
      <Dialog open={isSimulateDialogOpen} onOpenChange={setIsSimulateDialogOpen}>
        <DialogContent className="sm:max-w-[425px]">
          <DialogHeader>
            <DialogTitle>Simulate M-Pesa Transaction</DialogTitle>
            <DialogDescription>
              Enter details to simulate an M-Pesa transaction for testing.
            </DialogDescription>
          </DialogHeader>
          <div className="grid gap-4 py-4">
            <div className="grid grid-cols-4 items-center gap-4">
              <Label htmlFor="till_number" className="text-right">
                Till Number
              </Label>
              <Input
                id="till_number"
                value={simulateData.till_number}
                onChange={(e) => setSimulateData({ ...simulateData, till_number: e.target.value })}
                className="col-span-3"
                required
                disabled={!!user?.mpesa_till_number} // Disable if merchant has a till number
              />
            </div>
            <div className="grid grid-cols-4 items-center gap-4">
              <Label htmlFor="amount" className="text-right">
                Amount (Ksh)
              </Label>
              <Input
                id="amount"
                type="number"
                step="0.01"
                value={simulateData.amount}
                onChange={(e) => setSimulateData({ ...simulateData, amount: parseFloat(e.target.value) || 0 })}
                className="col-span-3"
                required
              />
            </div>
            <div className="grid grid-cols-4 items-center gap-4">
              <Label htmlFor="customer_phone" className="text-right">
                Customer Phone
              </Label>
              <Input
                id="customer_phone"
                type="tel"
                value={simulateData.customer_phone}
                onChange={(e) => setSimulateData({ ...simulateData, customer_phone: e.target.value })}
                className="col-span-3"
                required
              />
            </div>
            <div className="grid grid-cols-4 items-center gap-4">
              <Label htmlFor="customer_name" className="text-right">
                Customer Name
              </Label>
              <Input
                id="customer_name"
                value={simulateData.customer_name || ''}
                onChange={(e) => setSimulateData({ ...simulateData, customer_name: e.target.value })}
                className="col-span-3"
              />
            </div>
          </div>
          <DialogFooter>
            <Button type="submit" onClick={handleSimulateTransaction} disabled={simulating}>
              {simulating ? 'Simulating...' : 'Simulate Transaction'}
            </Button>
          </DialogFooter>
        </DialogContent>
      </Dialog>
    </div>
  );
};

export default TransactionsPage;