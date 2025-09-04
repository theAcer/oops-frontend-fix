"use client";

import React, { useRef, useEffect } from 'react';
import { Button, ButtonProps } from '@/components/ui/button';
import { gsap } from 'gsap';
import { cn } from '@/lib/utils';

interface AnimatedButtonProps extends Omit<ButtonProps, 'asChild'> {
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
      const tl = gsap.timeline();
      tl.to(sheen, { x: "100%", duration: 0.8, ease: "power1.out" }) // First pass
        .set(sheen, { x: "-100%" }) // Reset instantly
        .to(sheen, { x: "100%", duration: 0.8, ease: "power1.out", delay: 0.1 }); // Second pass with slight delay
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
      className={cn("relative overflow-hidden bg-gradient-to-r from-primary-start to-primary-end", className)}
      {...props}
    >
      <div
        ref={sheenRef}
        className="absolute inset-0 w-1/4 bg-white/30 transform -skew-x-12 pointer-events-none"
        style={{
          filter: 'blur(5px)',
          left: '-25%',
        }}
      />
      <span className="relative z-10">{children}</span>
    </Button>
  );
}