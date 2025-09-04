"use client";

import React from 'react';
import { Card, CardContent, CardHeader, CardTitle } from '../ui/card';
import { BarChart, Users, DollarSign, TrendingUp } from 'lucide-react';
import { OverviewMetrics } from '../../types/api';

interface OverviewCardsProps {
  overview: OverviewMetrics;
}

const OverviewCards = ({ overview }: OverviewCardsProps) => {
  return (
    <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-4">
      <Card>
        <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
          <CardTitle className="text-sm font-medium">Total Revenue</CardTitle>
          <DollarSign className="h-4 w-4 text-muted-foreground" />
        </CardHeader>
        <CardContent>
          <div className="text-2xl font-bold">Ksh {overview.total_revenue.toLocaleString('en-KE', { minimumFractionDigits: 2, maximumFractionDigits: 2 })}</div>
          <p className="text-xs text-muted-foreground">
            {overview.growth_metrics.revenue_growth >= 0 ? '+' : ''}
            {overview.growth_metrics.revenue_growth.toFixed(2)}% from last period
          </p>
        </CardContent>
      </Card>
      <Card>
        <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
          <CardTitle className="text-sm font-medium">Total Transactions</CardTitle>
          <BarChart className="h-4 w-4 text-muted-foreground" />
        </CardHeader>
        <CardContent>
          <div className="text-2xl font-bold">{overview.total_transactions.toLocaleString()}</div>
          <p className="text-xs text-muted-foreground">
            {overview.growth_metrics.transaction_growth >= 0 ? '+' : ''}
            {overview.growth_metrics.transaction_growth.toFixed(2)}% from last period
          </p>
        </CardContent>
      </Card>
      <Card>
        <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
          <CardTitle className="text-sm font-medium">Unique Customers</CardTitle>
          <Users className="h-4 w-4 text-muted-foreground" />
        </CardHeader>
        <CardContent>
          <div className="text-2xl font-bold">{overview.unique_customers.toLocaleString()}</div>
          <p className="text-xs text-muted-foreground">
            {overview.growth_metrics.customer_growth >= 0 ? '+' : ''}
            {overview.growth_metrics.customer_growth.toFixed(2)}% from last period
          </p>
        </CardContent>
      </Card>
      <Card>
        <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
          <CardTitle className="text-sm font-medium">Avg. Transaction Value</CardTitle>
          <TrendingUp className="h-4 w-4 text-muted-foreground" />
        </CardHeader>
        <CardContent>
          <div className="text-2xl font-bold">Ksh {overview.average_transaction_value.toLocaleString('en-KE', { minimumFractionDigits: 2, maximumFractionDigits: 2 })}</div>
          <p className="text-xs text-muted-foreground">
            {overview.growth_metrics.avg_value_growth >= 0 ? '+' : ''}
            {overview.growth_metrics.avg_value_growth.toFixed(2)}% from last period
          </p>
        </CardContent>
      </Card>
    </div>
  );
};

export default OverviewCards;