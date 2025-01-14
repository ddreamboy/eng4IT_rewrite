<!-- frontend/src/views/HomePage.vue -->
<template>
  <div>
    <!-- Приветствие и общий прогресс -->
    <header class="mb-8">
      <h1 class="text-2xl font-bold mb-2">
        {{ greeting }}, {{ authStore.user?.username || 'Гость' }}!
      </h1>
      <p class="text-light-accent dark:text-dark-accent">
        {{ dailyMessage }}
      </p>
    </header>

    <!-- Прогресс на сегодня -->
    <div v-if="authStore.isAuthenticated" class="mb-8">
      <div class="p-4 rounded-lg bg-light-secondary dark:bg-dark-secondary">
        <div class="flex items-center justify-between mb-2">
          <span class="text-sm font-medium">Дневная цель</span>
          <span class="text-sm text-light-accent dark:text-dark-accent"
            >{{ progress.completed }}/{{ progress.daily_goal }}</span
          >
        </div>
        <div class="h-2 rounded-full bg-light-primary dark:bg-dark-primary overflow-hidden">
          <div
            class="h-full bg-light-accent dark:bg-dark-accent transition-all"
            :style="{ width: `${progressPercentage}%` }"
          ></div>
        </div>
      </div>
    </div>

    <!-- Карточки заданий -->
    <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-2 gap-6">
      <TaskCard
        type="words"
        title="Перевод слов"
        description="Тренируйте перевод технических терминов и профессиональной лексики"
        stats="100+ слов"
        :progress="75"
        @start="navigateToTask('words')"
      />

      <TaskCard
        type="dialog"
        title="Диалоги"
        description="Практикуйте общение в реальных рабочих ситуациях"
        stats="10 диалогов"
        :progress="45"
        @start="navigateToTask('dialog')"
      />

      <TaskCard
        type="terms"
        title="Технические термины"
        description="Изучайте профессиональные термины с контекстом и примерами"
        stats="50+ терминов"
        :progress="60"
        @start="navigateToTask('terms')"
      />

      <TaskCard
        type="email"
        title="Деловая переписка"
        description="Учитесь составлять профессиональные email на английском"
        stats="5 шаблонов"
        :progress="30"
        @start="navigateToTask('email')"
      />
    </div>
  </div>
</template>

<script setup>
import { computed } from 'vue'
import { useRouter } from 'vue-router'
import { useAuthStore } from '../stores/authStore'

const router = useRouter()
const authStore = useAuthStore()

// Приветствие в зависимости от времени суток
const greeting = computed(() => {
  const hour = new Date().getHours()
  if (hour < 12) return 'Доброе утро'
  if (hour < 17) return 'Добрый день'
  return 'Добрый вечер'
})

// Временные данные (потом будут из API)
const progress = {
  completed: 7,
  daily_goal: 10,
}

const progressPercentage = computed(() =>
  Math.min(100, (progress.completed / progress.daily_goal) * 100),
)

const dailyMessage = computed(() => {
  if (!authStore.isAuthenticated) {
    return 'Войдите, чтобы начать обучение'
  }
  if (progress.completed >= progress.daily_goal) {
    return 'Дневная цель выполнена! 🎉'
  }
  return `Осталось ${progress.daily_goal - progress.completed} заданий до цели`
})

function navigateToTask(type) {
  if (!authStore.isAuthenticated) {
    router.push('/auth')
    return
  }

  switch (type) {
    case 'words':
    case 'terms':
      router.push(`/${type}`)
      break
    case 'dialog':
    case 'email':
      router.push(`/tasks?type=${type}`)
      break
  }
}
</script>
