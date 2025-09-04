"use client";

import React, { useState, useEffect } from 'react';
import { useAuth } from '../../context/AuthContext';
import api from '../../lib/api';
import { NotificationHistoryItem } from '../../types/api';
import { toast } from 'react-hot-toast';
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from '../../components/ui/card';
import { Alert, AlertDescription, AlertTitle } from '../../components/ui/alert';
import { Terminal } from 'lucide-react';
import { DataTable } from '../../components/ui/data-table';
import { ColumnDef } from '@tanstack/react-table';
import { Badge } from '../../components/ui/badge';
import { format } from 'date-fns';

// Define columns for the data table
const columns: ColumnDef<NotificationHistoryItem>[] = [
  {
    accessorKey: 'created_at',
    header: 'Date',
    cell: ({ row }) => format(new Date(row.getValue('created_at')), 'MMM dd, yyyy HH:mm'),
  },
  {
    accessorKey: 'type',
    header: 'Type',
    cell: ({ row }) => {
      const type: string = row.getValue('type');
      return <Badge variant="outline">{type.charAt(0).toUpperCase() + type.slice(1)}</Badge>;
    },
  },
  {
    accessorKey: 'recipient',
    header: 'Recipient',
  },
  {
    accessorKey: 'message',
    header: 'Message',
    cell: ({ row }) => <div className="max-w-xs truncate">{row.getValue('message')}</div>,
  },
  {
    accessorKey: 'status',
    header: 'Status',
    cell: ({ row }) => {
      const status: string = row.getValue('status');
      const getStatusColor = (status: string) => {
        switch (status.toLowerCase()) {
          case 'sent':
          case 'delivered':
            return 'bg-green-100 text-green-800';
          case 'failed':
          case 'bounced':
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
    accessorKey: 'cost',
    header: 'Cost (Ksh)',
    cell: ({ row }) => <div className="text-right">{row.getValue('cost').toFixed(2)}</div>,
  },
  {
    accessorKey: 'error',
    header: 'Error',
    cell: ({ row }) => <div className="max-w-xs truncate text-red-500">{row.getValue('error') || 'N/A'}</div>,
  },
];

const NotificationsPage = () => {
  const { user, loading: authLoading } = useAuth();
  const [notifications, setNotifications] = useState<NotificationHistoryItem[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    const fetchNotifications = async () => {
      if (!user?.merchant_id) {
        setLoading(false);
        return;
      }

      setLoading(true);
      setError(null);
      try {
        const response = await api.get<{ notifications: NotificationHistoryItem[]; count: number }>(
          `/api/v1/notifications/history/${user.merchant_id}`
        );
        setNotifications(response.data.notifications);
      } catch (err: any) {
        console.error('Failed to fetch notifications:', err);
        setError(err.response?.data?.detail || 'Failed to load notifications.');
        toast.error(err.response?.data?.detail || 'Failed to load notifications.');
      } finally {
        setLoading(false);
      }
    };

    if (!authLoading && user?.merchant_id) {
      fetchNotifications();
    }
  }, [authLoading, user?.merchant_id]);

  if (authLoading || loading) {
    return <div className="text-center py-8">Loading notifications...</div>;
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
            Please link a business to view notification history.
          </AlertDescription>
        </Alert>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      <h1 className="text-3xl font-bold">Notifications</h1>

      <Card>
        <CardHeader>
          <CardTitle>SMS Notification History</CardTitle>
          <CardDescription>
            Overview of all SMS messages sent from your account.
          </CardDescription>
        </CardHeader>
        <CardContent>
          <DataTable columns={columns} data={notifications} />
        </CardContent>
      </Card>
    </div>
  );
};

export default NotificationsPage;