// src/components/ThemeSwitcher.vue
<template>
    <button @click="store.toggleTheme()" class="p-2 rounded-lg transition-colors" :class="[
        store.isDark
            ? 'hover:bg-dark-primary/50 text-dark-accent'
            : 'hover:bg-light-primary/50 text-light-accent'
    ]">
        <Sun v-if="store.isDark" class="w-5 h-5" />
        <Moon v-else class="w-5 h-5" />
    </button>
</template>

<script setup>
import { Sun, Moon } from 'lucide-vue-next'
import { useThemeStore } from '@/stores/themeStore'

const store = useThemeStore()
</script>