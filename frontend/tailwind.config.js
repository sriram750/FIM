/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx}",
  ],
  darkMode: 'class',
  theme: {
    extend: {
      colors: {
        fim: {
          bg: "#0B0F17",
          panel: "#111827",
          surface: "#1A2234",
          border: "#1F293D",
          hover: "#26324D",
          primary: "#3B82F6",
          accent: "#60A5FA",
          cyan: "#06B6D4",
          emerald: "#10B981",
          amber: "#F59E0B",
          rose: "#F43F5E",
          text: "#F3F4F6",
          muted: "#9CA3AF",
        }
      }
    },
  },
  plugins: [],
}
