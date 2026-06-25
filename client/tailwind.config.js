/** @type {import('tailwindcss').Config} */
// Colors map to CSS variables (defined in index.css) so light/dark switches with a
// single [data-theme] attribute — no need to sprinkle dark: variants everywhere.
export default {
  content: ["./index.html", "./src/**/*.{ts,tsx}"],
  darkMode: ['selector', '[data-theme="dark"]'],
  theme: {
    extend: {
      colors: {
        primary: {
          DEFAULT: "var(--primary)",
          strong: "var(--primary-strong)",
          soft: "var(--primary-soft)",
        },
        accent: {
          DEFAULT: "var(--accent)",
          soft: "var(--accent-soft)",
        },
        danger: { DEFAULT: "var(--danger)", soft: "var(--danger-soft)" },
        warning: { DEFAULT: "var(--warning)", soft: "var(--warning-soft)" },
        success: { DEFAULT: "var(--success)", soft: "var(--success-soft)" },
        bg: { DEFAULT: "var(--bg)", elevated: "var(--bg-elevated)" },
        surface: { DEFAULT: "var(--surface)", 2: "var(--surface-2)" },
        border: "var(--border)",
        content: {
          DEFAULT: "var(--text)",
          muted: "var(--text-muted)",
          faint: "var(--text-faint)",
        },
      },
      fontFamily: {
        sans: ["Inter", "system-ui", "-apple-system", "Segoe UI", "Roboto", "sans-serif"],
      },
      borderRadius: {
        DEFAULT: "var(--radius)",
        lg: "var(--radius-lg)",
        md: "var(--radius)",
        sm: "var(--radius-sm)",
      },
      boxShadow: {
        sm: "var(--shadow-sm)",
        DEFAULT: "var(--shadow)",
      },
      maxWidth: {
        app: "1180px",
      },
      keyframes: {
        spin: { to: { transform: "rotate(360deg)" } },
      },
    },
  },
  plugins: [],
};
