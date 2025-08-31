import { type Config } from "tailwindcss";

export default {
  content: [
    "./src/pages/**/*.{js,ts,jsx,tsx,mdx}",
    "./src/components/**/*.{js,ts,jsx,tsx,mdx}",
    "./src/app/**/*.{js,ts,jsx,tsx,mdx}",
  ],
  darkMode: 'class', // Enable class-based dark mode
  theme: {
    extend: {
      colors: {
        background: "hsl(var(--color-background))",
        foreground: "hsl(var(--color-foreground))",
        card: "hsl(var(--color-card))",
        "card-foreground": "hsl(var(--color-card-foreground))",
        popover: "hsl(var(--color-popover))",
        "popover-foreground": "hsl(var(--color-popover-foreground))",
        primary: "hsl(var(--color-primary))",
        "primary-foreground": "hsl(var(--color-primary-foreground))",
        secondary: "hsl(var(--color-secondary))",
        "secondary-foreground": "hsl(var(--color-secondary-foreground))",
        muted: "hsl(var(--color-muted))",
        "muted-foreground": "hsl(var(--color-muted-foreground))",
        accent: "hsl(var(--color-accent))",
        "accent-foreground": "hsl(var(--color-accent-foreground))",
        destructive: "hsl(var(--color-destructive))",
        "destructive-foreground": "hsl(var(--color-destructive-foreground))",
        border: "hsl(var(--color-border))",
        input: "hsl(var(--color-input))",
        ring: "hsl(var(--color-ring))",
        "chart-1": "hsl(var(--color-chart-1))",
        "chart-2": "hsl(var(--color-chart-2))",
        "chart-3": "hsl(var(--color-chart-3))",
        "chart-4": "hsl(var(--color-chart-4))",
        "chart-5": "hsl(var(--color-chart-5))",
        success: "hsl(var(--color-success))",
        "success-foreground": "hsl(var(--color-success-foreground))",
        warning: "hsl(var(--color-warning))",
        "warning-foreground": "hsl(var(--color-warning-foreground))",
        "brand-primary": "hsl(var(--color-brand-primary))",
        "brand-secondary": "hsl(var(--color-brand-secondary))",
      },
      borderRadius: {
        lg: "var(--radius)",
        md: "calc(var(--radius) - 2px)",
        sm: "calc(var(--radius) - 4px)",
      },
      keyframes: {
        "accordion-down": {
          from: { height: "0" },
          to: { height: "var(--radix-accordion-content-height)" },
        },
        "accordion-up": {
          from: { height: "var(--radix-accordion-content-height)" },
          to: { height: "0" },
        },
      },
      animation: {
        "accordion-down": "accordion-down 0.2s ease-out",
        "accordion-up": "accordion-up 0.2s ease-out",
      },
    },
  },
  plugins: [require("tailwindcss-animate")],
} satisfies Config;