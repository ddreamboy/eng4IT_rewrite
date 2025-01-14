// src/stores/themeStore.js
import { defineStore } from 'pinia'
import { ref } from 'vue'

export const useThemeStore = defineStore('theme', () => {
  const currentTheme = ref(localStorage.getItem('theme') || 'dark')

  // Computed
  const isDark = ref(currentTheme.value === 'dark')
  const isLight = ref(currentTheme.value === 'light')

  // Actions
  function setTheme(theme) {
    currentTheme.value = theme
    localStorage.setItem('theme', theme)
    document.documentElement.classList.remove('dark', 'light')
    document.documentElement.classList.add(theme)
  }

  function toggleTheme() {
    const newTheme = currentTheme.value === 'dark' ? 'light' : 'dark'
    setTheme(newTheme)
  }

  // Initialize theme on store creation
  setTheme(currentTheme.value)

  return {
    currentTheme,
    isDark,
    isLight,
    toggleTheme
  }
})