"use client"

import useSWR from "swr"
import { apiService } from "@/services/api-service"
import { useAuth } from "@/contexts/auth-context"

export function useDashboardAnalytics() {
  const { user } = useAuth()
  const merchantId = user?.merchant_id

  return useSWR(
    merchantId ? `/analytics/dashboard/${merchantId}` : null,
    () => apiService.getDashboardAnalytics(merchantId!),
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
    () => apiService.getCustomers(merchantId!, page, limit),
  )
}

export function useCustomer(customerId: number | null) {
  return useSWR(
    customerId ? `/customers/${customerId}` : null,
    () => apiService.getCustomer(customerId!)
  )
}

export function useTransactions(filters?: {
  customer_id?: number
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

  return useSWR(key, () => apiService.getTransactions(merchantId!, filters))
}

export function useMerchant() {
  const { user } = useAuth()
  const merchantId = user?.merchant_id

  return useSWR(
    merchantId ? `/merchants/${merchantId}` : null,
    () => apiService.getMerchant(merchantId!)
  )
}

export function useRevenueAnalytics() {
  const { user } = useAuth()
  const merchantId = user?.merchant_id

  return useSWR(
    merchantId ? `/analytics/revenue/${merchantId}` : null,
    () => apiService.getRevenueAnalytics(merchantId!)
  )
}

export function useCustomerAnalytics() {
  const { user } = useAuth()
  const merchantId = user?.merchant_id

  return useSWR(
    merchantId ? `/analytics/customers/${merchantId}` : null,
    () => apiService.getCustomerAnalytics(merchantId!)
  )
}

export function useLoyaltyAnalytics() {
  const { user } = useAuth()
  const merchantId = user?.merchant_id

  return useSWR(
    merchantId ? `/analytics/loyalty/${merchantId}` : null,
    () => apiService.getLoyaltyAnalytics(merchantId!)
  )
}

export function useCustomerInsights() {
  const { user } = useAuth()
  const merchantId = user?.merchant_id

  return useSWR(
    merchantId ? `/analytics/customer-insights/${merchantId}` : null,
    () => apiService.getCustomerInsights(merchantId!)
  )
}

export function useChurnRisk() {
  const { user } = useAuth()
  const merchantId = user?.merchant_id

  return useSWR(
    merchantId ? `/analytics/churn-risk/${merchantId}` : null,
    () => apiService.getChurnRisk(merchantId!)
  )
}

export function useMerchantInsights() {
  const { user } = useAuth()
  const merchantId = user?.merchant_id

  return useSWR(
    merchantId ? `/ai/merchant/${merchantId}/insights` : null,
    () => apiService.getMerchantInsights(merchantId!)
  )
}

export function useRealTimeMetrics() {
  const { user } = useAuth()
  const merchantId = user?.merchant_id

  return useSWR(
    merchantId ? `/analytics/real-time/${merchantId}` : null,
    () => apiService.getRealTimeMetrics(merchantId!),
    {
      refreshInterval: 10000, // Refresh every 10 seconds
    },
  )
}

export function useCampaigns() {
  const { user } = useAuth()
  const merchantId = user?.merchant_id

  return useSWR(
    merchantId ? `/campaigns?merchant_id=${merchantId}` : null,
    () => apiService.getCampaigns ? apiService.getCampaigns(merchantId!) : Promise.resolve({ campaigns: [], total: 0 })
  )
}

export function useLoyaltyPrograms() {
  const { user } = useAuth()
  const merchantId = user?.merchant_id

  return useSWR(
    merchantId ? `/loyalty/programs?merchant_id=${merchantId}` : null,
    () => apiService.getLoyaltyPrograms ? apiService.getLoyaltyPrograms(merchantId!) : Promise.resolve({ programs: [], total: 0 })
  )
}