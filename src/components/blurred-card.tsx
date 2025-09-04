"use client";

import React from 'react';
import { Card, CardProps } from '@/components/ui/card';
import { cn } from '@/lib/utils';

interface BlurredCardProps extends CardProps {
  children: React.ReactNode;
  className?: string;
}

export function BlurredCard({ children, className, ...props }: BlurredCardProps) {
  return (
    <Card className={cn("bg-card/80 backdrop-blur-md border border-border/50 shadow-lg", className)} {...props}>
      {children}
    </Card>
  );
}