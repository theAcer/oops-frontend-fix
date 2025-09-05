"use client";

import React from 'react';
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from '../ui/card';
import { ScrollArea } from '../ui/scroll-area';
import { Avatar, AvatarFallback } from '../ui/avatar';
import { TransactionResponse } from '../../types/api';

interface RecentActivityProps {
  transactions: TransactionResponse[];
}

const RecentActivity = ({ transactions }: RecentActivityProps) => {
  return (
    <Card className="col-span-3">
      <CardHeader>
        <CardTitle>Recent Activity</CardTitle>
        <CardDescription>
          Your latest {transactions.length} transactions.
        </CardDescription>
      </CardHeader>
      <CardContent>
        <ScrollArea className="h-[350px]">
          <div className="space-y-8">
            {transactions.length === 0 ? (
              <p className="text-center text-muted-foreground">No recent transactions.</p>
            ) : (
              transactions.map((transaction) => (
                <div key={transaction.id} className="flex items-center">
                  <Avatar className="h-9 w-9">
                    <AvatarFallback>
                      {transaction.customer_name ? transaction.customer_name.charAt(0) : transaction.customer_phone.charAt(0)}
                    </AvatarFallback>
                  </Avatar>
                  <div className="ml-4 space-y-1">
                    <p className="text-sm font-medium leading-none">
                      {transaction.customer_name || `Customer ${transaction.customer_phone}`}
                    </p>
                    <p className="text-sm text-muted-foreground">
                      {transaction.mpesa_receipt_number}
                    </p>
                  </div>
                  <div className="ml-auto font-medium">
                    +Ksh {transaction.amount.toLocaleString('en-KE', { minimumFractionDigits: 2, maximumFractionDigits: 2 })}
                  </div>
                </div>
              ))
            )}
          </div>
        </ScrollArea>
      </CardContent>
    </Card>
  );
};

export default RecentActivity;