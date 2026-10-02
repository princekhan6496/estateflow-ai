import type { Config } from "tailwindcss";
export default {
  content: ["./app/**/*.{js,ts,jsx,tsx}", "./components/**/*.{js,ts,jsx,tsx}"],
  theme: {
    extend: { colors: { ink: "#171717", muted: "#6b7280", accent: "#285943" } },
  },
  plugins: [],
} satisfies Config;
