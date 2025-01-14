<!-- src/components/tasks/TaskCard.vue -->
<template>
  <div
    class="p-6 rounded-lg bg-light-secondary dark:bg-dark-secondary hover:scale-[1.02] transition-transform cursor-pointer"
    @click="$emit('click')"
  >
    <!-- Заголовок и иконка -->
    <div class="flex items-start justify-between mb-4">
      <div>
        <component :is="taskIcon" class="w-8 h-8 text-light-accent dark:text-dark-accent mb-3" />
        <h3 class="text-lg font-semibold">{{ title }}</h3>
      </div>

      <!-- Индикатор прогресса -->
      <div v-if="progress !== undefined" class="relative w-12 h-12">
        <svg class="transform -rotate-90 w-12 h-12">
          <circle
            cx="24"
            cy="24"
            r="20"
            stroke-width="4"
            fill="none"
            class="text-light-primary/10 dark:text-dark-primary/10"
            :stroke="currentColor"
          />
          <circle
            cx="24"
            cy="24"
            r="20"
            stroke-width="4"
            fill="none"
            :stroke="accentColor"
            :stroke-dasharray="circumference"
            :stroke-dashoffset="dashOffset"
            class="transition-all duration-500"
          />
        </svg>
        <span class="absolute inset-0 flex items-center justify-center text-sm font-medium">
          {{ progress }}%
        </span>
      </div>
    </div>

    <!-- Описание -->
    <p class="text-sm opacity-75 mb-4">{{ description }}</p>

    <!-- Дополнительный контент -->
    <slot name="extra" />

    <!-- Уровень сложности -->
    <div class="mt-4 flex items-center space-x-2 text-sm">
      <component :is="difficultyIcon" class="w-4 h-4" :class="difficultyColor" />
      <span :class="difficultyColor">{{ difficultyLabel }}</span>
    </div>
  </div>
</template>

<script setup>
import { computed } from 'vue'
import {
  BookOpen,
  Languages,
  GraduationCap,
  Mail,
  Dumbbell,
  Brain,
  Lightbulb,
} from 'lucide-vue-next'

const props = defineProps({
  title: {
    type: String,
    required: true,
  },
  description: {
    type: String,
    required: true,
  },
  type: {
    type: String,
    required: true,
    validator: (value) =>
      [
        'word-translation',
        'word-matching',
        'term-definition',
        'chat-dialog',
        'email-structure',
      ].includes(value),
  },
  difficulty: {
    type: String,
    required: true,
    validator: (value) => ['basic', 'intermediate', 'advanced'].includes(value),
  },
  progress: {
    type: Number,
    default: undefined,
  },
})

// Иконка задания
const taskIcon = computed(() => {
  const icons = {
    'word-translation': BookOpen,
    'word-matching': Languages,
    'term-definition': GraduationCap,
    'chat-dialog': Languages,
    'email-structure': Mail,
  }
  return icons[props.type]
})

// Стили сложности
const difficultyIcon = computed(() => {
  const icons = {
    basic: Dumbbell,
    intermediate: Brain,
    advanced: Lightbulb,
  }
  return icons[props.difficulty]
})

const difficultyLabel = computed(() => {
  const labels = {
    basic: 'Базовый',
    intermediate: 'Средний',
    advanced: 'Продвинутый',
  }
  return labels[props.difficulty]
})

const difficultyColor = computed(() => {
  const colors = {
    basic: 'text-green-500',
    intermediate: 'text-blue-500',
    advanced: 'text-purple-500',
  }
  return colors[props.difficulty]
})

// Расчёты для кругового прогресса
const circumference = 2 * Math.PI * 20
const dashOffset = computed(() => circumference - (props.progress / 100) * circumference)

const currentColor = computed(() => (props.progress >= 70 ? '#4ADE80' : '#60A5FA'))

const accentColor = computed(() => (props.progress >= 70 ? '#4ADE80' : '#60A5FA'))
</script>
