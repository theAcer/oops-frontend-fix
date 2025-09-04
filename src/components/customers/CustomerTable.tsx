"use client";

import React from 'react';
import { ColumnDef } from "@tanstack/react-table";
import { DataTable } from "../ui/data-table";
import { CustomerResponse } from '../../types/api';
import { Badge } from '../ui/badge';
import { Button } from '../ui/button';
import { ArrowUpDown, MoreHorizontal } from 'lucide-react';
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuLabel,
  DropdownMenuSeparator,
  DropdownMenuTrigger,
} from '../ui/dropdown-menu';

interface CustomerTableProps {
  customers: CustomerResponse[];
  onViewDetails: (customerId: number) => void;
  onEditCustomer: (customer: CustomerResponse) => void;
}

export const columns: ColumnDef<CustomerResponse>[] = [
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
    cell: ({ row, table }) => {
      const customer = row.original;
      const { onViewDetails, onEditCustomer } = table.options.meta as CustomerTableProps;

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
            <DropdownMenuItem>Send Offer</DropdownMenuItem>
          </DropdownMenuContent>
        </DropdownMenu>
      );
    },
  },
];

export function CustomerTable({ customers, onViewDetails, onEditCustomer }: CustomerTableProps) {
  return (
    <DataTable
      columns={columns}
      data={customers}
      meta={{ onViewDetails, onEditCustomer }}
      // Add filtering/pagination props if DataTable supports them
    />
  );
}