// tailwind.config.js
/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{vue,js,ts,jsx,tsx}",
    './src/components/**/*.{vue,js}',
    './src/views/**/*.{vue,js}',
  ],
  darkMode: 'class',
  theme: {
    extend: {
      colors: {
        // Темная тема
        'dark-primary': '#4B4033',  // Глубокий кофейный
        'dark-secondary': '#6B5841', // Светлый мокка
        'dark-accent': '#C7B29E',   // Мягкий кремовый
        'dark-text': '#EDE3D9',     // Песочный
        'dark-muted': '#A89787',    // Нежный серо-бежевый
        // Светлая тема
        'light-primary': '#FAF3E6', // Кремово-белый
        'light-secondary': '#EFE2D1', // Светлый песочный
        'light-accent': '#D4AF6A',   // Золотистый акцент
        'light-text': '#5A4633',     // Тёплый кофейный для текста
        'light-muted': '#C1A78D',    // Светло-бежевый с золотистым оттенком
        // Состояния
        'success': {
          light: '#A3C4A8',  // Светлый мятный
          dark: '#6D8B6A'    // Тёмный мятный
        },
        'warning': {
          light: '#D8B987',  // Светлый карамельный
          dark: '#B08C5C'    // Тёмный карамельный
        },
        'error': {
          light: '#D78A89',  // Светлый терракотовый
          dark: '#A66261'    // Тёмный терракотовый
        },
        'info': {
          light: '#B3C3C8',  // Светлый голубовато-серый
          dark: '#85979E'    // Тёмный голубовато-серый
        }
      }
      
    }
  },
  plugins: [],
}