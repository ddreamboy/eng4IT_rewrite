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
        // Dark theme - Серые оттенки как у Claude
        'dark': {
          'primary': '#1A1B1E',    // Глубокий серый
          'secondary': '#2B2C2F',  // Серый для контента
          'accent': '#D4B483',     // Золотистый акцент
          'text': '#FFFFFF',       // Белый текст
          'muted': '#A1A1AA',      // Приглушенный серый
        },
        
        // Light theme - Vanilla & Gold
        'light': {
          'primary': '#FFF9F0',    // Off-white
          'secondary': '#F5EBE0',  // Warm vanilla
          'accent': '#D4B483',     // Golden beige  
          'text': '#4A3728',       // Dark coffee
          'muted': '#BCA89B',      // Soft taupe
        },
      
        // States 
        'success': {
          light: '#9DC4A1',  // Sage green
          dark: '#5E7D61'    // Forest green
        },
        'warning': {
          light: '#E6C687',  // Warm gold
          dark: '#BC955C'    // Bronze
        },
        'error': {
          light: '#E59895',  // Dusty rose
          dark: '#B66E6B'    // Burgundy
        },
        'info': {
          light: '#A7BBC1',  // Steel blue
          dark: '#798D93'    // Slate
        }
      }
      
    }
  },
  plugins: [],
}