"use client"

import { ResponsiveContainer, LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, Legend } from "recharts"

interface RevenueChartProps {
  data: Array<{
    date: string
    revenue: number
    transactions: number
  }>
}

export function RevenueChart({ data }: RevenueChartProps) {
  return (
    <ResponsiveContainer width="100%" height={300}>
      <LineChart data={data}>
        <CartesianGrid strokeDasharray="3 3" />
        <XAxis dataKey="date" />
        <YAxis />
        <Tooltip
          formatter={(value, name) => [
            name === "revenue" ? `KES ${value.toLocaleString()}` : value,
            name === "revenue" ? "Revenue" : "Transactions",
          ]}
        />
        <Legend />
        <Line type="monotone" dataKey="revenue" stroke="#3b82f6" strokeWidth={2} name="Revenue" />
        <Line type="monotone" dataKey="transactions" stroke="#10b981" strokeWidth={2} name="Transactions" />
      </LineChart>
    </ResponsiveContainer>
  )
}
