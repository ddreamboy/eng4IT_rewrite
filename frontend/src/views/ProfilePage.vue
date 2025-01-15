// src/views/ProfilePage.vue
<template>
  <div class="container mx-auto px-4 py-8">
    <!-- Лоадер -->
    <div v-if="loading" class="flex justify-center items-center py-12">
      <div
        class="animate-spin rounded-full h-8 w-8 border-b-2"
        :class="[themeStore.isDark ? 'border-dark-accent' : 'border-light-accent']"
      ></div>
    </div>

    <!-- Ошибка -->
    <div v-else-if="error" class="text-center py-12">
      <p class="text-red-500">{{ error }}</p>
    </div>

    <!-- Профиль пользователя -->
    <div v-else class="max-w-2xl mx-auto">
      <!-- Заголовок и основная информация -->
      <div class="flex items-center mb-8">
        <div
          class="w-16 h-16 rounded-full flex items-center justify-center text-3xl font-bold mr-6"
          :class="[
            themeStore.isDark ? 'bg-dark-accent text-dark-text' : 'bg-light-accent text-light-text',
          ]"
        >
          {{ userInitials }}
        </div>
        <div>
          <h1
            class="text-2xl font-bold mb-1"
            :class="[themeStore.isDark ? 'text-dark-text' : 'text-light-text']"
          >
            {{ profile.username }}
          </h1>
          <p
            class="text-sm"
            :class="[themeStore.isDark ? 'text-dark-text/70' : 'text-light-text/70']"
          >
            {{ profile.email }}
          </p>
        </div>
      </div>

      <!-- Статистика аккаунта -->
      <div class="grid grid-cols-2 md:grid-cols-4 gap-4 mb-8">
        <StatCard
          title="Текущий уровень"
          :value="formatLevel(profile.current_level)"
          icon="AcademicCapIcon"
        />
        <StatCard title="Балл владения" :value="profile.proficiency_score" icon="ChartBarIcon" />
        <StatCard title="Дневная цель" :value="profile.daily_goal" icon="ClockIcon" />
        <StatCard title="Серия занятий" :value="profile.study_streak" icon="FireIcon" />
      </div>

      <!-- Расширенная статистика -->
      <div
        class="rounded-lg p-6"
        :class="[themeStore.isDark ? 'bg-dark-secondary' : 'bg-light-secondary']"
      >
        <h2
          class="text-xl font-semibold mb-4"
          :class="[themeStore.isDark ? 'text-dark-text' : 'text-light-text']"
        >
          Подробная статистика
        </h2>

        <div class="grid md:grid-cols-2 gap-4">
          <!-- Левая колонка -->
          <div>
            <StatDetailItem title="Всего заданий" :value="profile.statistics?.total_tasks || 0" />
            <StatDetailItem
              title="Выполненные задания"
              :value="profile.statistics?.completed_tasks || 0"
            />
            <StatDetailItem
              title="Точность"
              :value="`${(profile.statistics?.accuracy_rate * 100 || 0).toFixed(1)}%`"
            />
          </div>

          <!-- Правая колонка -->
          <div>
            <StatDetailItem title="Дата регистрации" :value="formatDate(profile.created_at)" />
            <StatDetailItem title="Последний вход" :value="formatDate(profile.last_login)" />
          </div>
        </div>

        <!-- Избранные слова -->
        <div class="mt-6">
          <h3
            class="text-lg font-semibold mb-3"
            :class="[themeStore.isDark ? 'text-dark-text' : 'text-light-text']"
          >
            Избранные слова
          </h3>
          <div v-if="profile.statistics?.favorite_words?.length" class="flex flex-wrap gap-2">
            <span
              v-for="word in profile.statistics.favorite_words"
              :key="word"
              class="px-2 py-1 rounded-full text-sm"
              :class="[
                themeStore.isDark
                  ? 'bg-dark-primary text-dark-text'
                  : 'bg-light-primary text-light-text',
              ]"
            >
              {{ word }}
            </span>
          </div>
          <p
            v-else
            class="text-sm"
            :class="[themeStore.isDark ? 'text-dark-text/50' : 'text-light-text/50']"
          >
            У вас пока нет избранных слов
          </p>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted, computed, defineComponent } from 'vue'
import { AcademicCapIcon, ChartBarIcon, ClockIcon, FireIcon } from '@heroicons/vue/24/outline'
import { useAuthStore } from '@/stores/authStore'
import { useThemeStore } from '@/stores/themeStore'
import axios from 'axios'

// Компонент статистической карточки
const StatCard = defineComponent({
  props: {
    title: String,
    value: [String, Number],
    icon: String,
  },
  setup(props) {
    const icons = {
      AcademicCapIcon,
      ChartBarIcon,
      ClockIcon,
      FireIcon,
    }
    const Icon = icons[props.icon]
    const themeStore = useThemeStore()

    return { props, Icon, themeStore }
  },
  template: `
    <div 
      class="rounded-lg p-4 flex flex-col items-center justify-center space-y-2 shadow-sm"
      :class="[
        themeStore.isDark 
          ? 'bg-dark-primary text-dark-text' 
          : 'bg-light-primary text-light-text'
      ]"
    >
      <component :is="Icon" class="w-6 h-6 opacity-70" />
      <div class="text-xl font-bold">{{ value }}</div>
      <div class="text-xs text-center opacity-70">{{ title }}</div>
    </div>
  `,
})

// Компонент детальной статистики
const StatDetailItem = defineComponent({
  props: {
    title: String,
    value: [String, Number],
  },
  setup() {
    const themeStore = useThemeStore()
    return { themeStore }
  },
  template: `
    <div 
      class="flex justify-between py-2 border-b"
      :class="[
        themeStore.isDark 
          ? 'border-dark-primary text-dark-text' 
          : 'border-light-primary text-light-text'
      ]"
    >
      <span class="opacity-70">{{ title }}</span>
      <span class="font-semibold">{{ value }}</span>
    </div>
  `,
})

// Стор для темы и авторизации
const authStore = useAuthStore()
const themeStore = useThemeStore()

// Состояние профиля
const profile = ref(null)
const loading = ref(true)
const error = ref(null)

// Инициализация данных
onMounted(async () => {
  try {
    const response = await axios.get('/api/v1/users/profile')
    profile.value = response.data
  } catch (err) {
    error.value = 'Не удалось загрузить профиль. Попробуйте позже.'
    console.error('Profile fetch error:', err)
  } finally {
    loading.value = false
  }
})

// Инициалы пользователя
const userInitials = computed(() => {
  if (!profile.value) return '?'
  const username = profile.value.username || ''
  return username
    .split(' ')
    .map((word) => word[0])
    .join('')
    .toUpperCase()
})

// Форматирование уровня
function formatLevel(level) {
  const levels = {
    beginner: 'Начинающий',
    basic: 'Базовый',
    intermediate: 'Средний',
    advanced: 'Продвинутый',
  }
  return levels[level] || level
}

// Форматирование даты
function formatDate(dateStr) {
  if (!dateStr) return '-'
  const date = new Date(dateStr)
  return date.toLocaleDateString('ru-RU', {
    day: 'numeric',
    month: 'long',
    year: 'numeric',
  })
}
</script>
