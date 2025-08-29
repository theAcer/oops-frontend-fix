"use client"

import useSWR from "swr"
import { apiService } from "@/services/api-service"
import { useAuth } from "@/contexts/auth-context"

export function useDashboardAnalytics() {
  const { user } = useAuth()
  const merchantId = user?.merchant_id

  return useSWR(
    merchantId ? `/analytics/dashboard/${merchantId}` : null,
    () => merchantId && apiService.getDashboardAnalytics(merchantId),
    {
      refreshInterval: 30000, // Refresh every 30 seconds
    },
  )
}

export function useCustomers(page = 1, limit = 10) {
  const { user } = useAuth()
  const merchantId = user?.merchant_id

  return useSWR(
    merchantId ? `/customers?merchant_id=${merchantId}&page=${page}&limit=${limit}` : null,
    () => merchantId && apiService.getCustomers(merchantId, page, limit),
  )
}

export function useCustomer(customerId: string | null) {
  return useSWR(customerId ? `/customers/${customerId}` : null, () => customerId && apiService.getCustomer(customerId))
}

export function useTransactions(filters?: {
  customer_id?: string
  start_date?: string
  end_date?: string
  page?: number
  limit?: number
}) {
  const { user } = useAuth()
  const merchantId = user?.merchant_id

  const key = merchantId
    ? `/transactions?merchant_id=${merchantId}&${new URLSearchParams(
        Object.entries(filters || {}).reduce(
          (acc, [key, value]) => {
            if (value !== undefined) acc[key] = value.toString()
            return acc
          },
          {} as Record<string, string>,
        ),
      ).toString()}`
    : null

  return useSWR(key, () => merchantId && apiService.getTransactions(merchantId, filters))
}

export function useMerchant() {
  const { user } = useAuth()
  const merchantId = user?.merchant_id

  return useSWR(merchantId ? `/merchants/${merchantId}` : null, () => merchantId && apiService.getMerchant(merchantId))
}

export function useRevenueAnalytics() {
  const { user } = useAuth()
  const merchantId = user?.merchant_id

  return useSWR(
    merchantId ? `/analytics/revenue/${merchantId}` : null,
    () => merchantId && apiService.getRevenueAnalytics(merchantId),
  )
}

export function useCustomerAnalytics() {
  const { user } = useAuth()
  const merchantId = user?.merchant_id

  return useSWR(
    merchantId ? `/analytics/customers/${merchantId}` : null,
    () => merchantId && apiService.getCustomerAnalytics(merchantId),
  )
}

export function useLoyaltyAnalytics() {
  const { user } = useAuth()
  const merchantId = user?.merchant_id

  return useSWR(
    merchantId ? `/analytics/loyalty/${merchantId}` : null,
    () => merchantId && apiService.getLoyaltyAnalytics(merchantId),
  )
}

export function useCustomerInsights() {
  const { user } = useAuth()
  const merchantId = user?.merchant_id

  return useSWR(
    merchantId ? `/analytics/customer-insights/${merchantId}` : null,
    () => merchantId && apiService.getCustomerInsights(merchantId),
  )
}

export function useChurnRisk() {
  const { user } = useAuth()
  const merchantId = user?.merchant_id

  return useSWR(
    merchantId ? `/analytics/churn-risk/${merchantId}` : null,
    () => merchantId && apiService.getChurnRisk(merchantId),
  )
}

export function useMerchantInsights() {
  const { user } = useAuth()
  const merchantId = user?.merchant_id

  return useSWR(
    merchantId ? `/ai/merchant/${merchantId}/insights` : null,
    () => merchantId && apiService.getMerchantInsights(merchantId),
  )
}

export function useRealTimeMetrics() {
  const { user } = useAuth()
  const merchantId = user?.merchant_id

  return useSWR(
    merchantId ? `/analytics/real-time/${merchantId}` : null,
    () => merchantId && apiService.getRealTimeMetrics(merchantId),
    {
      refreshInterval: 10000, // Refresh every 10 seconds
    },
  )
}
