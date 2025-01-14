// frontend/tailwind.config.js
/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{vue,js,ts,jsx,tsx}",
  ],
  theme: {
    extend: {
      colors: {
        // Темная тема
        'dark': {
          'primary': '#1a1a1a',
          'secondary': '#2D2D2D',
          'accent': '#4ADE80',
        },
        // Светлая тема
        'light': {
          'primary': '#ffffff',
          'secondary': '#f3f4f6',
          'accent': '#059669',
        },
        // Карамельная тема
        'candy': {
          'primary': '#FFF5E6',
          'secondary': '#FFE8CC',
          'accent': '#FFB6C1',
        }
      }
    },
  },
  plugins: [],
}