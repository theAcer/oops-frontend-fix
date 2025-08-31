"use client";

import React from 'react';
import { useTheme } from '@/contexts/theme-context';

interface ThemeWrapperProps {
  children: React.ReactNode;
}

export function ThemeWrapper({ children }: ThemeWrapperProps) {
  const { theme } = useTheme();

  return (
    <div
      className="min-h-screen w-full relative bg-background" // Apply bg-background directly
    >
      {children}
    </div>
  );
}