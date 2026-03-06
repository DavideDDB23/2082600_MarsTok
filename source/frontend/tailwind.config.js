/** @type {import('tailwindcss').Config} */
export default {
  content: ["./index.html", "./src/**/*.{ts,tsx}"],
  theme: {
    extend: {
      colors: {
        mars: {
          50:  "#fff3ee",
          100: "#ffe4d1",
          200: "#ffc5a0",
          300: "#ff9c66",
          400: "#ff6b2b",
          500: "#e84c0a",
          600: "#c93c07",
          700: "#a52e09",
          800: "#872710",
          900: "#6f2212",
        },
      },
    },
  },
  plugins: [],
};
