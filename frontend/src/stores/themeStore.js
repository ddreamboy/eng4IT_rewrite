// src/stores/themeStore.js
import { defineStore } from 'pinia'
import { ref, watch } from 'vue'

export const useThemeStore = defineStore('theme', () => {
  const currentTheme = ref(localStorage.getItem('theme') || 'dark')

  const isDark = ref(currentTheme.value === 'dark')

  // Следим за изменениями темы
  watch(currentTheme, (newTheme) => {
    isDark.value = newTheme === 'dark'
    localStorage.setItem('theme', newTheme)
    updateTheme()
  }, { immediate: true })

  function updateTheme() {
    // Удаляем все классы тем
    document.documentElement.classList.remove('dark', 'light')
    // Добавляем текущий класс темы
    document.documentElement.classList.add(currentTheme.value)
  }

  function toggleTheme() {
    currentTheme.value = currentTheme.value === 'dark' ? 'light' : 'dark'
  }

  // Инициализация при создании стора
  updateTheme()

  return {
    currentTheme,
    isDark,
    toggleTheme
  }
})