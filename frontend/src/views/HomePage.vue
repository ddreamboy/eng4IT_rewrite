// src/views/HomePage.vue
<template>
    <div class="min-h-[calc(100vh-4rem)] p-6">
        <h1 class="text-2xl font-bold mb-4">Добро пожаловать, {{ username }}!</h1>
        <p class="text-gray-600 dark:text-gray-400">
            Это главная страница приложения.
        </p>
    </div>
</template>

<script setup>
import { computed } from 'vue'
import { useAuthStore } from '@/stores/authStore'

const authStore = useAuthStore()
const username = computed(() => authStore.user?.username || 'Гость')
</script>