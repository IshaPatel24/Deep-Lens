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
        dark: {
          bg: "#080B16",
          card: "#101424",
          border: "#1D233D",
          hover: "#181E36"
        },
        primary: {
          50: '#F0F3FF',
          100: '#E1E7FF',
          500: '#5A67D8',
          600: '#4C51BF',
          700: '#434190',
        },
        accent: {
          cyan: '#00D8F6',
          purple: '#9F7AEA',
          pink: '#ED64A6',
          amber: '#ECC94B',
          emerald: '#38A169',
          crimson: '#E53E3E'
        }
      },
      fontFamily: {
        sans: ['Outfit', 'Inter', 'sans-serif'],
        mono: ['JetBrains Mono', 'monospace']
      },
      animation: {
        'pulse-slow': 'pulse 3s cubic-bezier(0.4, 0, 0.6, 1) infinite',
        'shimmer': 'shimmer 2s linear infinite',
      },
      keyframes: {
        shimmer: {
          '0%': { backgroundPosition: '-200% 0' },
          '100%': { backgroundPosition: '200% 0' },
        }
      }
    },
  },
  plugins: [],
}
