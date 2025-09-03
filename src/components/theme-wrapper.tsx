"use client";

import React from 'react';
import { useTheme } from '@/contexts/theme-context';
import { cn } from '@/lib/utils';

interface ThemeWrapperProps {
  children: React.ReactNode;
}

export function ThemeWrapper({ children }: ThemeWrapperProps) {
  const { theme } = useTheme();

  return (
    <div
      className={cn(
        "min-h-screen w-full relative",
        theme === 'dark' ? 'dark' : 'light' // Explicitly apply theme class
      )}
    >
      {children}
    </div>
  );
}