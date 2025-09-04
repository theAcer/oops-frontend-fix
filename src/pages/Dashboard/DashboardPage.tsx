"use client";

import React, { useState, useEffect } from 'react';
import { useAuth } from '../../context/AuthContext';
import { Card, CardHeader, CardTitle, CardContent, CardDescription } from '../../components/ui/card';
import { Alert, AlertDescription, AlertTitle } from '../../components/ui/alert';
import { Terminal } from 'lucide-react';
import api from '../../lib/api';
import { DashboardResponse, OverviewMetrics, DailyRevenueTrend, TransactionResponse } from '../../types/api';
import { toast } from 'react-hot-toast';
import OverviewCards from '../../components/dashboard/OverviewCards';
import RevenueChart from '../../components/dashboard/RevenueChart';
import RecentActivity from '../../components/dashboard/RecentActivity';

const DashboardPage = () => {
  const { user, loading: authLoading, isAuthenticated } = useAuth();
  const [dashboardData, setDashboardData] = useState<DashboardResponse | null>(null);
  const [dataLoading, setDataLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    const fetchDashboardData = async () => {
      if (!user?.merchant_id) {
        setDataLoading(false);
        return;
      }

      setDataLoading(true);
      setError(null);
      try {
        // Fetch data for the last 30 days
        const response = await api.get<DashboardResponse>(`/api/v1/analytics/dashboard/${user.merchant_id}?days=30`);
        setDashboardData(response.data);
      } catch (err: any) {
        console.error('Failed to fetch dashboard data:', err);
        setError(err.response?.data?.detail || 'Failed to load dashboard data.');
        toast.error(err.response?.data?.detail || 'Failed to load dashboard data.');
      } finally {
        setDataLoading(false);
      }
    };

    if (!authLoading && isAuthenticated) {
      fetchDashboardData();
    }
  }, [authLoading, isAuthenticated, user?.merchant_id]);

  if (authLoading || dataLoading) {
    return <div className="text-center py-8">Loading dashboard...</div>;
  }

  if (!isAuthenticated) {
    return <div className="text-center py-8">Please log in to view the dashboard.</div>;
  }

  if (!user?.merchant_id) {
    return (
      <div className="space-y-6">
        <h1 className="text-3xl font-bold">Welcome, {user?.name || user?.email}!</h1>
        <Alert>
          <Terminal className="h-4 w-4" />
          <AlertTitle>No Merchant Linked!</AlertTitle>
          <AlertDescription>
            Your account is not yet linked to a merchant. Please{' '}
            <a href="/link-merchant" className="underline font-medium">
              create or link a business
            </a>{' '}
            to access full dashboard features.
          </AlertDescription>
        </Alert>
      </div>
    );
  }

  if (error) {
    return (
      <Alert variant="destructive">
        <Terminal className="h-4 w-4" />
        <AlertTitle>Error</AlertTitle>
        <AlertDescription>{error}</AlertDescription>
      </Alert>
    );
  }

  if (!dashboardData) {
    return <div className="text-center py-8 text-muted-foreground">No dashboard data available.</div>;
  }

  // Extract data for components
  const overviewMetrics: OverviewMetrics = dashboardData.overview;
  const revenueTrendData: DailyRevenueTrend[] = dashboardData.revenue.daily_trend;
  // For recent activity, we'll fetch transactions directly as the dashboard endpoint doesn't return them
  // For now, let's use a placeholder or fetch separately if needed.
  // For simplicity, I'll add a separate fetch for recent transactions here.
  const [recentTransactions, setRecentTransactions] = useState<TransactionResponse[]>([]);
  const [transactionsLoading, setTransactionsLoading] = useState(true);

  useEffect(() => {
    const fetchRecentTransactions = async () => {
      if (!user?.merchant_id) {
        setTransactionsLoading(false);
        return;
      }
      setTransactionsLoading(true);
      try {
        const response = await api.get<TransactionResponse[]>(`/api/v1/transactions?merchant_id=${user.merchant_id}&limit=10`);
        setRecentTransactions(response.data);
      } catch (err) {
        console.error('Failed to fetch recent transactions:', err);
        toast.error('Failed to load recent transactions.');
      } finally {
        setTransactionsLoading(false);
      }
    };

    if (user?.merchant_id) {
      fetchRecentTransactions();
    }
  }, [user?.merchant_id]);


  return (
    <div className="space-y-6">
      <h1 className="text-3xl font-bold">Welcome, {user?.name || user?.email}!</h1>

      <OverviewCards overview={overviewMetrics} />

      <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-7">
        <RevenueChart data={revenueTrendData} />
        <RecentActivity transactions={recentTransactions} />
      </div>
    </div>
  );
};

export default DashboardPage;