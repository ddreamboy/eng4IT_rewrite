<!-- src/views/ProfilePage.vue -->
<template>
  <div class="space-y-6">
    <!-- Основная информация -->
    <div class="p-6 rounded-lg bg-light-secondary dark:bg-dark-secondary">
      <div class="flex items-center space-x-4 mb-6">
        <div
          class="w-16 h-16 rounded-full bg-light-accent dark:bg-dark-accent flex items-center justify-center"
        >
          <span class="text-xl font-bold text-white">{{ authStore.userInitials }}</span>
        </div>
        <div>
          <h1 class="text-2xl font-bold">{{ profile?.username }}</h1>
          <p class="text-light-accent dark:text-dark-accent">{{ profile?.email }}</p>
        </div>
      </div>

      <!-- Ключевые метрики -->
      <div class="grid grid-cols-1 md:grid-cols-4 gap-4 mb-6">
        <div class="p-4 rounded-lg bg-light-primary/5 dark:bg-dark-primary/5">
          <p class="text-sm opacity-75 mb-1">Уровень</p>
          <p class="text-lg font-semibold">{{ profile?.current_level }}</p>
        </div>
        <div class="p-4 rounded-lg bg-light-primary/5 dark:bg-dark-primary/5">
          <p class="text-sm opacity-75 mb-1">Мастерство</p>
          <p class="text-lg font-semibold">{{ profile?.proficiency_score.toFixed(1) }}%</p>
        </div>
        <div class="p-4 rounded-lg bg-light-primary/5 dark:bg-dark-primary/5">
          <p class="text-sm opacity-75 mb-1">Серия дней</p>
          <p class="text-lg font-semibold">{{ profile?.study_streak }} дней</p>
        </div>
        <div class="p-4 rounded-lg bg-light-primary/5 dark:bg-dark-primary/5">
          <p class="text-sm opacity-75 mb-1">Дневная цель</p>
          <p class="text-lg font-semibold">{{ profile?.daily_goal }} заданий</p>
        </div>
      </div>
    </div>

    <!-- Статистика -->
    <div class="grid grid-cols-1 md:grid-cols-2 gap-6">
      <!-- Прогресс по категориям -->
      <div class="p-6 rounded-lg bg-light-secondary dark:bg-dark-secondary">
        <h2 class="text-lg font-semibold mb-4">Прогресс по категориям</h2>
        <div class="space-y-4">
          <div
            v-for="(progress, category) in profile?.statistics?.category_progress"
            :key="category"
            class="space-y-2"
          >
            <div class="flex justify-between text-sm">
              <span class="capitalize">{{ category }}</span>
              <span>{{ progress.toFixed(1) }}%</span>
            </div>
            <div class="h-2 rounded-full bg-light-primary/10 dark:bg-dark-primary/10">
              <div
                class="h-full rounded-full bg-light-accent dark:bg-dark-accent transition-all"
                :style="{ width: `${progress}%` }"
              ></div>
            </div>
          </div>
        </div>
      </div>

      <!-- Статистика выполнения -->
      <div class="p-6 rounded-lg bg-light-secondary dark:bg-dark-secondary">
        <h2 class="text-lg font-semibold mb-4">Общая статистика</h2>
        <div class="space-y-4">
          <div class="flex justify-between items-center">
            <span>Всего заданий</span>
            <span class="font-semibold">{{ profile?.statistics?.total_tasks }}</span>
          </div>
          <div class="flex justify-between items-center">
            <span>Выполнено успешно</span>
            <span class="font-semibold">{{ profile?.statistics?.completed_tasks }}</span>
          </div>
          <div class="flex justify-between items-center">
            <span>Точность выполнения</span>
            <span class="font-semibold">{{ profile?.statistics?.accuracy_rate.toFixed(1) }}%</span>
          </div>
          <div class="flex justify-between items-center">
            <span>Дата регистрации</span>
            <span class="font-semibold">{{ formatDate(profile?.created_at) }}</span>
          </div>
        </div>
      </div>

      <!-- Избранные слова -->
      <div class="p-6 rounded-lg bg-light-secondary dark:bg-dark-secondary md:col-span-2">
        <h2 class="text-lg font-semibold mb-4">Избранные слова</h2>
        <div class="flex flex-wrap gap-2">
          <span
            v-for="word in profile?.statistics?.favorite_words"
            :key="word"
            class="px-3 py-1 rounded-full bg-light-primary/10 dark:bg-dark-primary/10"
          >
            {{ word }}
          </span>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useAuthStore } from '../stores/authStore'
import axios from 'axios'

const authStore = useAuthStore()
const profile = ref(null)

// Загрузка данных профиля
async function loadProfile() {
  try {
    const response = await axios.get('/api/v1/users/profile')
    profile.value = response.data
  } catch (error) {
    console.error('Error loading profile:', error)
  }
}

// Форматирование даты
function formatDate(date) {
  if (!date) return ''
  return new Date(date).toLocaleDateString('ru-RU', {
    year: 'numeric',
    month: 'long',
    day: 'numeric',
  })
}

onMounted(() => {
  loadProfile()
})
</script>
