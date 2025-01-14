// tailwind.config.js
/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{vue,js,ts,jsx,tsx}",
  ],
  darkMode: 'class',
  theme: {
    extend: {
      colors: {
        // Темная тема
        'dark-primary': '#0F172A',
        'dark-secondary': '#1E293B',
        'dark-accent': '#38BDF8',
        'dark-text': '#F8FAFC',
        'dark-muted': '#94A3B8',
        // Светлая тема
        'light-primary': '#FFFFFF',
        'light-secondary': '#F1F5F9',
        'light-accent': '#0EA5E9',
        'light-text': '#0F172A',
        'light-muted': '#64748B',
        // Состояния
        'success': {
          light: '#10B981',
          dark: '#059669'
        },
        'warning': {
          light: '#F59E0B',
          dark: '#D97706'
        },
        'error': {
          light: '#EF4444',
          dark: '#DC2626'
        },
        'info': {
          light: '#3B82F6',
          dark: '#2563EB'
        }
      }
    }
  },
  plugins: [],
}