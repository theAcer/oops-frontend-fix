"use client";

import React, { useRef, useEffect } from 'react';
import { Button, ButtonProps } from '@/components/ui/button';
import { gsap } from 'gsap';
import { cn } from '@/lib/utils';

interface AnimatedButtonProps extends ButtonProps {
  children: React.ReactNode;
  className?: string;
}

export function AnimatedButton({ children, className, ...props }: AnimatedButtonProps) {
  const buttonRef = useRef<HTMLButtonElement>(null);
  const sheenRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    const button = buttonRef.current;
    const sheen = sheenRef.current;

    if (!button || !sheen) return;

    gsap.set(sheen, { x: "-100%" });

    const handleMouseEnter = () => {
      gsap.to(sheen, {
        x: "100%",
        duration: 0.8,
        ease: "power1.out",
      });
    };

    const handleMouseLeave = () => {
      gsap.set(sheen, { x: "-100%" });
    };

    button.addEventListener('mouseenter', handleMouseEnter);
    button.addEventListener('mouseleave', handleMouseLeave);

    return () => {
      button.removeEventListener('mouseenter', handleMouseEnter);
      button.removeEventListener('mouseleave', handleMouseLeave);
    };
  }, []);

  return (
    <Button
      ref={buttonRef}
      className={cn(
        "relative overflow-hidden bg-gradient-primary text-primary-foreground shadow-elegant hover:shadow-glow transition-all duration-300",
        className
      )}
      {...props}
    >
      <div
        ref={sheenRef}
        className="absolute inset-0 w-1/4 bg-white/30 transform -skew-x-12 pointer-events-none"
        style={{
          filter: 'blur(5px)',
          left: '-25%', // Start off-screen to the left
        }}
      />
      <span className="relative z-10">{children}</span>
    </Button>
  );
}