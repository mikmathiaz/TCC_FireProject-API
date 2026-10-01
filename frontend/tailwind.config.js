/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx}",
  ],
  theme: {
    extend: {
      colors: {
        ember: {
          900: '#3a0d0d',
          800: '#731a1a',
          700: '#a62626',
          500: '#e64a19',
          400: '#ff7043',
        }
      }
    },
  },
  plugins: [],
}
