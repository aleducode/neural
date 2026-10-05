/** @type {import('tailwindcss').Config} */
export default {
  darkMode: ["class", '[data-theme="dark"]'],
  content: ["./src/**/*.{ts,tsx}", "./dev/**/*.{ts,tsx,html}", "../neural/manager/templates/**/*.html"],
  theme: {
    extend: {
      colors: {
        border: "hsl(var(--border))",
        input: "hsl(var(--input))",
        ring: "hsl(var(--ring))",
        background: "hsl(var(--background))",
        foreground: "hsl(var(--foreground))",
        faint: "hsl(var(--faint))",
        primary: {
          DEFAULT: "hsl(var(--primary))",
          foreground: "hsl(var(--primary-foreground))",
        },
        secondary: {
          DEFAULT: "hsl(var(--secondary))",
          foreground: "hsl(var(--secondary-foreground))",
        },
        muted: {
          DEFAULT: "hsl(var(--muted))",
          foreground: "hsl(var(--muted-foreground))",
        },
        destructive: {
          DEFAULT: "hsl(var(--destructive))",
          foreground: "hsl(var(--destructive-foreground))",
        },
        accent: {
          DEFAULT: "hsl(var(--accent))",
          foreground: "hsl(var(--accent-foreground))",
        },
        card: {
          DEFAULT: "hsl(var(--card))",
          foreground: "hsl(var(--card-foreground))",
        },
        popover: {
          DEFAULT: "hsl(var(--popover))",
          foreground: "hsl(var(--popover-foreground))",
        },
        // Pares de estado del diseño: fondo + tinta, siempre juntos.
        positive: {
          DEFAULT: "hsl(var(--positive))",
          soft: "hsl(var(--positive-soft))",
        },
        negative: {
          DEFAULT: "hsl(var(--negative))",
          soft: "hsl(var(--negative-soft))",
          strong: "hsl(var(--negative-strong))",
          "strong-soft": "hsl(var(--negative-strong-soft))",
        },
        warning: {
          DEFAULT: "hsl(var(--warning))",
          soft: "hsl(var(--warning-soft))",
        },
        sidebar: {
          DEFAULT: "hsl(var(--sidebar-background))",
          foreground: "hsl(var(--sidebar-foreground))",
          primary: "hsl(var(--sidebar-primary))",
          "primary-foreground": "hsl(var(--sidebar-primary-foreground))",
          accent: "hsl(var(--sidebar-accent))",
          "accent-foreground": "hsl(var(--sidebar-accent-foreground))",
          border: "hsl(var(--sidebar-border))",
          ring: "hsl(var(--sidebar-ring))",
        },
      },
      // La escala del .pen: 16 tarjeta, 12 tarjeta anidada, 8 boton e item,
      // 4 checkbox. Los componentes de shadcn piden lg/md/sm, asi que la
      // escala se dobla a esos tres nombres en vez de dejar los de shadcn.
      borderRadius: {
        lg: "var(--radius)",
        xl: "calc(var(--radius) - 0.25rem)",
        md: "0.5rem",
        sm: "0.25rem",
      },
      boxShadow: {
        widget: "0 1px 1.75px 0 rgb(13 13 18 / 0.06)",
        pop: "0 16px 28px 0 rgb(13 13 18 / 0.10)",
        // Caja de icono del KPI: luz interna arriba + sombra corta abajo.
        "icon-box":
          "inset 0 -4px 5.25px 0 rgb(255 255 255 / 0.50), 0 1px 1.75px 0 rgb(13 13 18 / 0.10)",
      },
      fontSize: {
        // El .pen usa 12/14/16/18/20/24 con lineHeight propio por tamaño.
        xs: ["0.75rem", { lineHeight: "1.5" }],
        sm: ["0.875rem", { lineHeight: "1.5" }],
        base: ["1rem", { lineHeight: "1.5" }],
        lg: ["1.125rem", { lineHeight: "1.35" }],
        xl: ["1.25rem", { lineHeight: "1.35" }],
        "2xl": ["1.5rem", { lineHeight: "1.3" }],
      },
    },
  },
  plugins: [],
};
