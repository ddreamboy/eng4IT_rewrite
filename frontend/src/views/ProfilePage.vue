// src/views/ProfilePage.vue
<template>
  <div class="container mx-auto px-4 py-8 h-screen flex flex-col">
    <!-- Лоадер -->
    <div v-if="loading" class="flex justify-center items-center py-12">
      <div class="animate-spin rounded-full h-8 w-8 border-b-2"
        :class="[themeStore.isDark ? 'border-dark-accent' : 'border-light-accent']"></div>
    </div>

    <!-- Ошибка -->
    <div v-else-if="error" class="text-center py-12">
      <p class="text-red-500">{{ error }}</p>
    </div>

    <!-- Профиль пользователя -->
    <div v-else class="max-w-2xl mx-auto flex-1 overflow-y-auto">
      <!-- Заголовок и основная информация -->
      <div class="flex items-center mb-8">
        <div class="w-16 h-16 rounded-full flex items-center justify-center text-3xl font-bold mr-6" :class="[
          themeStore.isDark ? 'bg-dark-accent text-dark-text' : 'bg-light-accent text-light-text',
        ]">
          {{ userInitials }}
        </div>
        <div>
          <h1 class="text-2xl font-bold mb-1" :class="[themeStore.isDark ? 'text-dark-text' : 'text-light-text']">
            {{ profile.username }}
          </h1>
          <p class="text-sm" :class="[themeStore.isDark ? 'text-dark-text/70' : 'text-light-text/70']">
            {{ profile.email }}
          </p>
        </div>
      </div>

      <!-- Статистика аккаунта -->
      <div class="grid grid-cols-2 md:grid-cols-4 gap-4 mb-2">
        <StatCard title="Текущий уровень" :value="formatLevel(profile.current_level)" icon="AcademicCapIcon" />
        <StatCard title="Балл владения" :value="profile.proficiency_score" icon="ChartBarIcon" />
        <StatCard title="Дневная цель" :value="profile.daily_goal" icon="ClockIcon" />
        <StatCard title="Серия занятий" :value="profile.study_streak" icon="FireIcon" />
      </div>

      <!-- Расширенная статистика -->
      <div class="rounded-lg p-6" :class="[themeStore.isDark ? 'bg-dark-secondary' : 'bg-light-secondary']">
        <!-- Избранные слова -->
        <h1 class="text-lg font-semibold mb-3" :class="[themeStore.isDark ? 'text-dark-text' : 'text-light-text']">
          Избранные слова
        </h1>
        <div v-if="profile.statistics?.favorite_words?.length" class="flex flex-wrap gap-2">
          <span v-for="word in profile.statistics.favorite_words" :key="word" class="px-2 py-1 rounded-full text-sm"
            :class="[
              themeStore.isDark
                ? 'bg-dark-primary text-dark-text'
                : 'bg-light-primary text-light-text',
            ]">
            {{ word }}
          </span>
        </div>
        <p v-else class="text-sm" :class="[themeStore.isDark ? 'text-dark-text/50' : 'text-light-text/50']">
          У вас пока нет избранных слов
        </p>
      </div>

      <!-- Прогресс обучения -->
      <div class="mt-8">
        <h2 class="text-xl font-semibold mb-4" :class="[themeStore.isDark ? 'text-dark-text' : 'text-light-text']">
          Прогресс обучения
        </h2>

        <!-- Прогресс по категориям -->
        <div class="rounded-lg p-6 mb-6" :class="[themeStore.isDark ? 'bg-dark-secondary' : 'bg-light-secondary']">
          <h3 class="text-lg font-semibold mb-4" :class="[themeStore.isDark ? 'text-dark-text' : 'text-light-text']">
            Прогресс по категориям
          </h3>
          <div class="grid gap-4">
            <div v-for="(progress, category) in profile.statistics?.category_progress" :key="category"
              class="flex items-center">
              <span class="w-48 text-sm" :class="[themeStore.isDark ? 'text-dark-text' : 'text-light-text']">
                {{ category }}
              </span>
              <div class="flex-1 h-2 bg-gray-200 rounded-full overflow-hidden">
                <div class="h-full transition-all duration-300"
                  :class="[themeStore.isDark ? 'bg-dark-accent' : 'bg-light-accent']"
                  :style="{ width: `${progress}%` }" />
              </div>
              <span class="ml-3 text-sm" :class="[themeStore.isDark ? 'text-dark-text' : 'text-light-text']">
                {{ Math.round(progress) }}%
              </span>
            </div>
          </div>
        </div>

        <!-- Изученные слова -->
        <div class="rounded-lg p-6" :class="[themeStore.isDark ? 'bg-dark-secondary' : 'bg-light-secondary']">
          <h3 class="text-lg font-semibold mb-4" :class="[themeStore.isDark ? 'text-dark-text' : 'text-light-text']">
            Последние изученные слова
          </h3>
          <div class="grid md:grid-cols-2 gap-4">
            <div v-for="word in profile.statistics?.detailed_stats?.words" :key="word.id" class="p-4 rounded-lg"
              :class="[themeStore.isDark ? 'bg-dark-primary' : 'bg-light-primary']">
              <div class="flex justify-between items-start mb-2">
                <div>
                  <h4 class="font-semibold" :class="[themeStore.isDark ? 'text-dark-text' : 'text-light-text']">
                    {{ word.word }}
                  </h4>
                  <p class="text-sm" :class="[themeStore.isDark ? 'text-dark-text/70' : 'text-light-text/70']">
                    {{ word.type }} • {{ word.difficulty }}
                  </p>
                </div>
                <button @click="toggleFavorite(word)" :class="[
                  'text-yellow-500',
                  word.is_favorite ? 'opacity-100' : 'opacity-50 hover:opacity-75'
                ]">
                  ★
                </button>
              </div>
              <div class="flex items-center mt-2">
                <span class="text-sm mr-2" :class="[themeStore.isDark ? 'text-dark-text/70' : 'text-light-text/70']">
                  Уровень освоения:
                </span>
                <div class="flex-1 h-2 bg-gray-200 rounded-full overflow-hidden">
                  <div class="h-full transition-all duration-300"
                    :class="[themeStore.isDark ? 'bg-dark-accent' : 'bg-light-accent']"
                    :style="{ width: `${(word.mastery_level / 5) * 100}%` }" />
                </div>
              </div>
            </div>
          </div>
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

// Сторы для темы и авторизации
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

// Работа с избранными словами
async function toggleFavorite(word) {
  try {
    await axios.post(`/api/v1/words/${word.id}/toggle-favorite`)
    word.is_favorite = !word.is_favorite
  } catch (err) {
    console.error('Failed to toggle favorite status:', err)
  }
}

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
<style>
.overflow-y-auto {
  scrollbar-width: thin;
  scrollbar-color: rgba(155, 155, 155, 0.5) transparent;
}

.overflow-y-auto::-webkit-scrollbar {
  width: 6px;
}

.overflow-y-auto::-webkit-scrollbar-track {
  background: transparent;
}

.overflow-y-auto::-webkit-scrollbar-thumb {
  background-color: rgba(155, 155, 155, 0.5);
  border-radius: 3px;
}

.overflow-y-auto::-webkit-scrollbar-thumb:hover {
  background-color: rgba(155, 155, 155, 0.7);
}
</style>