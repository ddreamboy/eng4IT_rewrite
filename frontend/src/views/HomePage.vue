// src/views/HomePage.vue
<template>
  <div class="min-h-[calc(100vh-4rem)]">
    <div class="max-w-screen-xl mx-auto">
      <!-- Приветствие -->
      <header class="mb-8">
        <h1
          class="text-2xl font-bold mb-2"
          :class="[themeStore.isDark ? 'text-dark-text' : 'text-light-text']"
        >
          Добро пожаловать, {{ username }}!
        </h1>
        <p class="text-gray-600 dark:text-gray-400">
          Выберите задание для изучения технического английского
        </p>
      </header>

      <!-- Лоадер -->
      <div v-if="loading" class="flex justify-center items-center py-12">
        <div
          class="animate-spin rounded-full h-8 w-8 border-b-2"
          :class="[themeStore.isDark ? 'border-dark-accent' : 'border-light-accent']"
        ></div>
      </div>

      <!-- Сетка с заданиями -->
      <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6 h-full">
        <TaskCard v-for="task in tasks" :key="task.id" :task="task" />
      </div>

      <!-- Ошибка -->
      <div v-if="error" class="text-center py-12">
        <p class="text-red-500">{{ error }}</p>
        <button
          @click="fetchTasks"
          class="mt-4 px-4 py-2 rounded-lg transition-colors"
          :class="[
            themeStore.isDark
              ? 'bg-dark-accent hover:bg-dark-accent/90 text-dark-text'
              : 'bg-light-accent hover:bg-light-accent/90 text-light-text',
          ]"
        >
          Попробовать снова
        </button>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { useAuthStore } from '@/stores/authStore'
import { useThemeStore } from '@/stores/themeStore'
import TaskCard from '@/components/TaskCard.vue'
import axios from 'axios'

const profile = ref(null)

const authStore = useAuthStore()
const themeStore = useThemeStore()

const tasks = ref([])
const loading = ref(true)
const error = ref(null)

// Изменяем computed свойство для username
const username = computed(() => {
  if (profile.value?.username) {
    return profile.value.username
  }
  return authStore.user?.username || 'Гость'
})

// Добавляем загрузку профиля
async function fetchProfile() {
  try {
    const response = await axios.get('/api/v1/users/profile')
    profile.value = response.data
  } catch (err) {
    console.error('Error fetching profile:', err)
  }
}

async function fetchTasks() {
  loading.value = true
  error.value = null

  try {
    const response = await axios.get('/api/v1/tasks/info')
    console.log('API Response:', response.data) // Для отладки
    tasks.value = Array.isArray(response.data) ? response.data : []
  } catch (err) {
    error.value = 'Не удалось загрузить задания. Попробуйте позже.'
    console.error('Error fetching tasks:', err)
  } finally {
    loading.value = false
  }
}

onMounted(() => {
  fetchTasks()
  fetchProfile()
})
</script>
