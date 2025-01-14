// frontend/src/stores/themeStore.js
import { defineStore } from 'pinia'

export const useThemeStore = defineStore('theme', {
  state: () => ({
    currentTheme: localStorage.getItem('theme') || 'dark', // dark | light | candy
  }),

  getters: {
    isDark: (state) => state.currentTheme === 'dark',
    isLight: (state) => state.currentTheme === 'light',
    isCandy: (state) => state.currentTheme === 'candy',
  },

  actions: {
    setTheme(theme) {
      this.currentTheme = theme
      localStorage.setItem('theme', theme)

      // Управляем классами для Tailwind
      const root = document.documentElement
      root.classList.remove('dark', 'light', 'candy')
      root.classList.add(theme)
    },

    toggleTheme() {
      const themes = ['dark', 'light', 'candy']
      const currentIndex = themes.indexOf(this.currentTheme)
      const nextIndex = (currentIndex + 1) % themes.length
      this.setTheme(themes[nextIndex])
    },

    initTheme() {
      this.setTheme(this.currentTheme)
    },
  },
})
