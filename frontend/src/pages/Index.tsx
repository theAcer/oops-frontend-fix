"use client";

import React, { useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';

const IndexPage = () => {
  const { isAuthenticated, loading, user } = useAuth();
  const navigate = useNavigate();

  useEffect(() => {
    if (!loading) {
      if (isAuthenticated) {
        if (user?.merchant_id) {
          navigate('/dashboard');
        } else {
          navigate('/link-merchant');
        }
      } else {
        navigate('/login');
      }
    }
  }, [isAuthenticated, loading, user, navigate]);

  return (
    <div className="flex items-center justify-center min-h-[calc(100vh-4rem)]">
      <p>Loading application...</p>
    </div>
  );
};

export default IndexPage;