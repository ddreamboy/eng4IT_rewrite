// tailwind.config.js
/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{vue,js,ts,jsx,tsx}",
  ],
  darkMode: 'class', // Важно для работы темы
  theme: {
    extend: {
      colors: {
        'dark': {
          'primary': '#1a1a1a',
          'secondary': '#2D2D2D',
          'accent': '#4ADE80',
        },
        'light': {
          'primary': '#ffffff',
          'secondary': '#f3f4f6',
          'accent': '#059669',
        },
        'candy': {
          'primary': '#FFF5E6',
          'secondary': '#FFE8CC',
          'accent': '#FFB6C1',
        }
      },
      container: {
        center: true,
        padding: {
          DEFAULT: '1rem',
          sm: '2rem',
          lg: '4rem',
          xl: '5rem',
          '2xl': '6rem',
        },
      }
    },
  },
  plugins: [],
}