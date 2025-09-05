"use client"

import { ResponsiveContainer, BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, Legend } from "recharts"

interface CustomerChartProps {
  data: Array<{
    month: string
    new_customers: number
    returning_customers: number
  }>
}

export function CustomerChart({ data }: CustomerChartProps) {
  return (
    <ResponsiveContainer width="100%" height={300}>
      <BarChart data={data}>
        <CartesianGrid strokeDasharray="3 3" />
        <XAxis dataKey="month" />
        <YAxis />
        <Tooltip />
        <Legend />
        <Bar dataKey="new_customers" fill="#3b82f6" name="New Customers" />
        <Bar dataKey="returning_customers" fill="#10b981" name="Returning Customers" />
      </BarChart>
    </ResponsiveContainer>
  )
}