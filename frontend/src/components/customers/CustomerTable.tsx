"use client";

import React, { useState } from 'react';
import { ColumnDef } from "@tanstack/react-table";
import { DataTable } from "../ui/data-table";
import { CustomerResponse } from '../../types/api';
import { Badge } from '../ui/badge';
import { Button } from '../ui/button';
import { ArrowUpDown, MoreHorizontal, MessageSquare } from 'lucide-react';
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuLabel,
  DropdownMenuSeparator,
  DropdownMenuTrigger,
} from '../ui/dropdown-menu';
import { Dialog, DialogContent, DialogHeader, DialogTitle, DialogDescription, DialogFooter } from '../ui/dialog';
import { Label } from '../ui/label';
import { Textarea } from '../ui/textarea';
import api from '../../lib/api';
import { toast } from 'react-hot-toast';
import { useAuth } from '../../context/AuthContext';

interface CustomerTableProps {
  customers: CustomerResponse[];
  onViewDetails: (customerId: number) => void;
  onEditCustomer: (customer: CustomerResponse) => void;
}

export function CustomerTable({ customers, onViewDetails, onEditCustomer }: CustomerTableProps) {
  const { user } = useAuth();
  const [isSendSMSDialogOpen, setIsSendSMSDialogOpen] = useState(false);
  const [selectedCustomer, setSelectedCustomer] = useState<CustomerResponse | null>(null);
  const [smsMessage, setSmsMessage] = useState('');
  const [sendingSMS, setSendingSMS] = useState(false);

  const handleSendSMSClick = (customer: CustomerResponse) => {
    setSelectedCustomer(customer);
    setIsSendSMSDialogOpen(true);
  };

  const handleSendSMS = async () => {
    if (!selectedCustomer || !user?.merchant_id || !smsMessage.trim()) {
      toast.error('Invalid customer, merchant, or empty message.');
      return;
    }

    setSendingSMS(true);
    try {
      await api.post(`/api/v1/notifications/sms/send/${user.merchant_id}`, {
        phone_number: selectedCustomer.phone,
        message: smsMessage,
        customer_id: selectedCustomer.id,
        notification_type: 'promotional', // Default to promotional
      });
      toast.success(`SMS sent to ${selectedCustomer.name || selectedCustomer.phone}!`);
      setIsSendSMSDialogOpen(false);
      setSmsMessage('');
    } catch (err: any) {
      console.error('Failed to send SMS:', err);
      toast.error(err.response?.data?.detail || 'Failed to send SMS.');
    } finally {
      setSendingSMS(false);
    }
  };

  const columns: ColumnDef<CustomerResponse>[] = [
    {
      accessorKey: "name",
      header: ({ column }) => {
        return (
          <Button
            variant="ghost"
            onClick={() => column.toggleSorting(column.getIsSorted() === "asc")}
          >
            Name
            <ArrowUpDown className="ml-2 h-4 w-4" />
          </Button>
        );
      },
      cell: ({ row }) => {
        const customer = row.original;
        return (
          <div className="flex items-center">
            <span className="font-medium">{customer.name || "N/A"}</span>
          </div>
        );
      },
    },
    {
      accessorKey: "phone",
      header: "Phone",
    },
    {
      accessorKey: "email",
      header: "Email",
      cell: ({ row }) => <div className="lowercase">{row.getValue("email") || "N/A"}</div>,
    },
    {
      accessorKey: "loyalty_points",
      header: ({ column }) => {
        return (
          <Button
            variant="ghost"
            onClick={() => column.toggleSorting(column.getIsSorted() === "asc")}
          >
            Points
            <ArrowUpDown className="ml-2 h-4 w-4" />
          </Button>
        );
      },
      cell: ({ row }) => <div className="text-right font-medium">{row.getValue("loyalty_points")}</div>,
    },
    {
      accessorKey: "loyalty_tier",
      header: "Tier",
      cell: ({ row }) => {
        const tier: string = row.getValue("loyalty_tier");
        const getTierColor = (tier: string) => {
          switch (tier.toLowerCase()) {
            case 'bronze': return 'bg-amber-100 text-amber-800';
            case 'silver': return 'bg-gray-100 text-gray-800';
            case 'gold': return 'bg-yellow-100 text-yellow-800';
            case 'platinum': return 'bg-blue-100 text-blue-800';
            default: return 'bg-gray-100 text-gray-800';
          }
        };
        return <Badge className={getTierColor(tier)}>{tier.charAt(0).toUpperCase() + tier.slice(1)}</Badge>;
      },
    },
    {
      accessorKey: "total_spent",
      header: () => <div className="text-right">Total Spent</div>,
      cell: ({ row }) => {
        const amount = parseFloat(row.getValue("total_spent"));
        const formatted = new Intl.NumberFormat("en-KE", {
          style: "currency",
          currency: "KES",
        }).format(amount);

        return <div className="text-right font-medium">{formatted}</div>;
      },
    },
    {
      id: "actions",
      enableHiding: false,
      cell: ({ row }) => { // Removed table from destructuring
        const customer = row.original;
        // Access onViewDetails and onEditCustomer directly from props
        return (
          <DropdownMenu>
            <DropdownMenuTrigger asChild>
              <Button variant="ghost" className="h-8 w-8 p-0">
                <span className="sr-only">Open menu</span>
                <MoreHorizontal className="h-4 w-4" />
              </Button>
            </DropdownMenuTrigger>
            <DropdownMenuContent align="end">
              <DropdownMenuLabel>Actions</DropdownMenuLabel>
              <DropdownMenuItem onClick={() => onViewDetails(customer.id)}>
                View Details
              </DropdownMenuItem>
              <DropdownMenuItem onClick={() => onEditCustomer(customer)}>
                Edit Customer
              </DropdownMenuItem>
              <DropdownMenuSeparator />
              <DropdownMenuItem onClick={() => handleSendSMSClick(customer)}>
                <MessageSquare className="mr-2 h-4 w-4" /> Send SMS
              </DropdownMenuItem>
              <DropdownMenuItem>Send Offer</DropdownMenuItem>
            </DropdownMenuContent>
          </DropdownMenu>
        );
      },
    },
  ];

  return (
    <>
      <DataTable
        columns={columns}
        data={customers}
        // Pass props directly if DataTable doesn't use meta for actions
      />

      {/* Send SMS Dialog */}
      <Dialog open={isSendSMSDialogOpen} onOpenChange={setIsSendSMSDialogOpen}>
        <DialogContent className="sm:max-w-[425px]">
          <DialogHeader>
            <DialogTitle>Send SMS to {selectedCustomer?.name || selectedCustomer?.phone}</DialogTitle>
            <DialogDescription>
              Compose a message to send to this customer.
            </DialogDescription>
          </DialogHeader>
          <div className="grid gap-4 py-4">
            <div className="grid gap-2">
              <Label htmlFor="smsMessage">Message</Label>
              <Textarea
                id="smsMessage"
                placeholder="Type your message here..."
                value={smsMessage}
                onChange={(e) => setSmsMessage(e.target.value)}
                rows={5}
                required
              />
            </div>
          </div>
          <DialogFooter>
            <Button type="submit" onClick={handleSendSMS} disabled={sendingSMS}>
              {sendingSMS ? 'Sending...' : 'Send SMS'}
            </Button>
          </DialogFooter>
        </DialogContent>
      </Dialog>
    </>
  );
}