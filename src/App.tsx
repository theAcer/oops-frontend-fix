"use client";

import React from 'react';
import { BrowserRouter as Router, Routes, Route, Navigate } from 'react-router-dom';
import { AuthProvider, useAuth } from './context/AuthContext';
import Layout from './components/Layout';
import LoginPage from './pages/Auth/LoginPage';
import RegisterPage from './pages/Auth/RegisterPage';
import LinkMerchantPage from './pages/Auth/LinkMerchantPage';
import DashboardPage from './pages/Dashboard/DashboardPage';
import IndexPage from './pages/Index';
import { Toaster } from 'react-hot-toast'; // For toast notifications

// Placeholder for other pages
const CustomersPage = () => <div className="p-4">Customers Page (Coming Soon!)</div>;
const LoyaltyPage = () => <div className="p-4">Loyalty Page (Coming Soon!)</div>;
const CampaignsPage = () => <div className="p-4">Campaigns Page (Coming Soon!)</div>;
const NotificationsPage = () => <div className="p-4">Notifications Page (Coming Soon!)</div>;
const SettingsPage = () => <div className="p-4">Settings Page (Coming Soon!)</div>;

// A component to protect routes
const ProtectedRoute = ({ children }: { children: JSX.Element }) => {
  const { isAuthenticated, loading, user } = useAuth();

  if (loading) {
    return <div className="text-center py-8">Loading...</div>;
  }

  if (!isAuthenticated) {
    return <Navigate to="/login" replace />;
  }

  // If authenticated but no merchant, redirect to link merchant page
  if (!user?.merchant_id && window.location.pathname !== '/link-merchant') {
    return <Navigate to="/link-merchant" replace />;
  }

  return children;
};

function App() {
  return (
    <Router>
      <AuthProvider>
        <Toaster /> {/* Toast notifications */}
        <Layout>
          <Routes>
            <Route path="/" element={<IndexPage />} />
            <Route path="/login" element={<LoginPage />} />
            <Route path="/register" element={<RegisterPage />} />
            <Route
              path="/link-merchant"
              element={
                <ProtectedRoute>
                  <LinkMerchantPage />
                </ProtectedRoute>
              }
            />
            <Route
              path="/dashboard"
              element={
                <ProtectedRoute>
                  <DashboardPage />
                </ProtectedRoute>
              }
            />
            <Route
              path="/customers"
              element={
                <ProtectedRoute>
                  <CustomersPage />
                </ProtectedRoute>
              }
            />
            <Route
              path="/loyalty"
              element={
                <ProtectedRoute>
                  <LoyaltyPage />
                </ProtectedRoute>
              }
            />
            <Route
              path="/campaigns"
              element={
                <ProtectedRoute>
                  <CampaignsPage />
                </ProtectedRoute>
              }
            />
            <Route
              path="/notifications"
              element={
                <ProtectedRoute>
                  <NotificationsPage />
                </ProtectedRoute>
              }
            />
            <Route
              path="/settings"
              element={
                <ProtectedRoute>
                  <SettingsPage />
                </ProtectedRoute>
              }
            />
          </Routes>
        </Layout>
      </AuthProvider>
    </Router>
  );
}

export default App;