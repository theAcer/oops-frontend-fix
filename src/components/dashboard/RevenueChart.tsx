"use client";

import React from 'react';
import {
  ResponsiveContainer,
  LineChart,
  Line,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  Legend,
} from 'recharts';
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from '../ui/card';
import { DailyRevenueTrend } from '../../types/api';

interface RevenueChartProps {
  data: DailyRevenueTrend[];
}

const RevenueChart = ({ data }: RevenueChartProps) => {
  // Format data for chart: ensure dates are sorted and in a readable format
  const formattedData = data
    .map((item) => ({
      ...item,
      date: new Date(item.date).toLocaleDateString('en-KE', { month: 'short', day: 'numeric' }),
    }))
    .sort((a, b) => new Date(a.date).getTime() - new Date(b.date).getTime());

  return (
    <Card className="col-span-4">
      <CardHeader>
        <CardTitle>Revenue Trends</CardTitle>
        <CardDescription>Revenue and transactions over the last 30 days.</CardDescription>
      </CardHeader>
      <CardContent className="pl-2">
        <div className="h-[350px]">
          <ResponsiveContainer width="100%" height="100%">
            <LineChart
              data={formattedData}
              margin={{
                top: 5,
                right: 10,
                left: 10,
                bottom: 5,
              }}
            >
              <CartesianGrid strokeDasharray="3 3" className="stroke-muted" />
              <XAxis
                dataKey="date"
                stroke="#888888"
                fontSize={12}
                tickLine={false}
                axisLine={false}
              />
              <YAxis
                yAxisId="left"
                stroke="#888888"
                fontSize={12}
                tickLine={false}
                axisLine={false}
                tickFormatter={(value) => `Ksh ${value.toLocaleString()}`}
              />
              <YAxis
                yAxisId="right"
                orientation="right"
                stroke="#888888"
                fontSize={12}
                tickLine={false}
                axisLine={false}
                tickFormatter={(value) => `${value.toLocaleString()} Txns`}
              />
              <Tooltip
                formatter={(value: number, name: string) => {
                  if (name === 'revenue') {
                    return [`Ksh ${value.toLocaleString('en-KE', { minimumFractionDigits: 2, maximumFractionDigits: 2 })}`, 'Revenue'];
                  }
                  if (name === 'transactions') {
                    return [`${value.toLocaleString()} Txns`, 'Transactions'];
                  }
                  return [value.toLocaleString(), name];
                }}
                labelFormatter={(label) => `Date: ${label}`}
                contentStyle={{ backgroundColor: 'hsl(var(--background))', border: '1px solid hsl(var(--border))', borderRadius: '0.5rem' }}
                labelStyle={{ color: 'hsl(var(--foreground))' }}
              />
              <Legend />
              <Line
                yAxisId="left"
                type="monotone"
                dataKey="revenue"
                stroke="hsl(var(--primary))"
                activeDot={{ r: 8 }}
                name="Revenue"
              />
              <Line
                yAxisId="right"
                type="monotone"
                dataKey="transactions"
                stroke="hsl(var(--secondary-foreground))"
                activeDot={{ r: 8 }}
                name="Transactions"
              />
            </LineChart>
          </ResponsiveContainer>
        </div>
      </CardContent>
    </Card>
  );
};

export default RevenueChart;