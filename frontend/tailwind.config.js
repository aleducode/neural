/** @type {import('tailwindcss').Config} */
export default {
  content: ["./src/**/*.{ts,tsx}", "../neural/manager/templates/**/*.html"],
  // manager.css sigue vistiendo las pantallas que todavia no son islas, asi
  // que el reset de Tailwind no puede entrar a pisarlas.
  corePlugins: { preflight: false },
  theme: {
    extend: {
      colors: {
        border: "hsl(var(--mgr-border))",
        input: "hsl(var(--mgr-input))",
        ring: "hsl(var(--mgr-ring))",
        background: "hsl(var(--mgr-background))",
        foreground: "hsl(var(--mgr-foreground))",
        primary: {
          DEFAULT: "hsl(var(--mgr-primary))",
          foreground: "hsl(var(--mgr-primary-foreground))",
        },
        secondary: {
          DEFAULT: "hsl(var(--mgr-secondary))",
          foreground: "hsl(var(--mgr-secondary-foreground))",
        },
        muted: {
          DEFAULT: "hsl(var(--mgr-muted))",
          foreground: "hsl(var(--mgr-muted-foreground))",
        },
        destructive: {
          DEFAULT: "hsl(var(--mgr-destructive))",
          foreground: "hsl(var(--mgr-destructive-foreground))",
        },
        success: {
          DEFAULT: "hsl(var(--mgr-success))",
          foreground: "hsl(var(--mgr-success-foreground))",
        },
      },
      borderRadius: {
        lg: "var(--mgr-radius)",
        md: "calc(var(--mgr-radius) - 2px)",
        sm: "calc(var(--mgr-radius) - 4px)",
      },
    },
  },
  plugins: [],
};
