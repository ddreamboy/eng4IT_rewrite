<!-- frontend/src/components/ThemeSwitcher.vue -->
<template>
  <div class="relative">
    <button
      @click="store.toggleTheme()"
      class="p-2 rounded-lg hover:bg-light-secondary dark:hover:bg-dark-secondary transition-colors"
      :title="buttonTitle"
    >
      <Sun v-if="store.isDark" class="w-5 h-5 text-light-accent" />
      <Moon v-else-if="store.isLight" class="w-5 h-5 text-dark-accent" />
      <Candy v-else class="w-5 h-5 text-candy-accent" />
    </button>
  </div>
</template>

<script setup>
import { computed } from 'vue'
import { Sun, Moon, Candy } from 'lucide-vue-next'
import { useThemeStore } from '../stores/themeStore'

const store = useThemeStore()

const buttonTitle = computed(() => {
  switch (store.currentTheme) {
    case 'dark':
      return 'Переключить на светлую тему'
    case 'light':
      return 'Переключить на карамельную тему'
    default:
      return 'Переключить на тёмную тему'
  }
})
</script>
