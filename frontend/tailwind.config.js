/** @type {import('tailwindcss').Config} */
module.exports = {
  darkMode: 'class',
  content: [
    './pages/**/*.{js,ts,jsx,tsx,mdx}',
    './components/**/*.{js,ts,jsx,tsx,mdx}',
    './app/**/*.{js,ts,jsx,tsx,mdx}',
  ],
  theme: {
    extend: {
      colors: {
        dark: {
          bg: '#111827',
          card: '#1f2937',
          border: '#374151',
        },
        light: {
          bg: '#f9fafb',
          card: '#ffffff',
          border: '#e5e7eb',
        }
      }
    },
  },
  plugins: [],
};
