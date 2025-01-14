<!-- src/components/tasks/TaskList.vue -->
<template>
  <div>
    <!-- Состояние загрузки -->
    <div v-if="isLoading" class="flex justify-center items-center py-12">
      <LoaderIcon class="w-8 h-8 animate-spin text-light-accent dark:text-dark-accent" />
    </div>

    <!-- Список заданий -->
    <div v-else class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
      <TaskCard
        v-for="task in tasks"
        :key="task.id"
        :title="task.title"
        :description="task.description"
        :type="type"
        :difficulty="task.difficulty"
        :progress="task.progress"
        @click="$emit('select', task)"
      >
        <!-- Слот для дополнительного контента -->
        <template #extra v-if="task.extra">
          <div class="text-sm text-gray-500 mt-2">
            {{ task.extra }}
          </div>
        </template>
      </TaskCard>

      <!-- Карточка для создания нового задания -->
      <button
        @click="generateNewTask"
        class="p-6 rounded-lg border-2 border-dashed border-light-primary/20 dark:border-dark-primary/20 hover:border-light-accent dark:hover:border-dark-accent transition-colors duration-200 text-center"
      >
        <PlusCircleIcon class="w-8 h-8 mx-auto mb-2 text-light-accent dark:text-dark-accent" />
        <span class="text-sm font-medium">Создать новое задание</span>
      </button>
    </div>

    <!-- Сообщение об ошибке -->
    <div
      v-if="error"
      class="mt-4 p-4 rounded-lg bg-red-50 dark:bg-red-900/20 text-red-600 dark:text-red-400"
    >
      {{ error }}
    </div>

    <!-- Пагинация -->
    <div v-if="totalPages > 1" class="mt-6 flex justify-center space-x-2">
      <button
        v-for="page in totalPages"
        :key="page"
        @click="currentPage = page"
        class="px-4 py-2 rounded-lg"
        :class="
          page === currentPage
            ? 'bg-light-accent dark:bg-dark-accent text-white'
            : 'bg-light-primary/10 dark:bg-dark-primary/10'
        "
      >
        {{ page }}
      </button>
    </div>
  </div>
</template>

<script setup>
import { ref, watchEffect } from 'vue'
import { LoaderIcon, PlusCircleIcon } from 'lucide-vue-next'
import TaskCard from './TaskCard.vue'
import axios from 'axios'

const props = defineProps({
  type: {
    type: String,
    required: true,
  },
  filters: {
    type: Object,
    required: true,
  },
  customParams: {
    type: Object,
    default: null,
  },
})

const emit = defineEmits(['select'])

// Состояние
const tasks = ref([])
const isLoading = ref(false)
const error = ref(null)
const currentPage = ref(1)
const totalPages = ref(1)

// Генерация задания
async function generateNewTask() {
  isLoading.value = true
  error.value = null

  try {
    // Определяем параметры запроса
    const params = props.customParams || generateDefaultParams()

    // Делаем запрос к API
    const response = await axios.post(`/api/v1/tasks/generate/${props.type}`, params)

    // Добавляем новое задание в начало списка
    tasks.value.unshift({
      id: Date.now(), // временный ID
      title: getTaskTitle(props.type),
      description: getTaskDescription(response.data),
      difficulty: props.filters.difficulty,
      progress: 0,
      content: response.data,
    })
  } catch (e) {
    error.value = e.response?.data?.detail || 'Ошибка при создании задания'
  } finally {
    isLoading.value = false
  }
}

// Загрузка заданий при изменении фильтров
watchEffect(async () => {
  if (isLoading.value) return

  isLoading.value = true
  error.value = null

  try {
    // Здесь будет запрос к API для получения списка заданий
    // Пока используем моковые данные
    await new Promise((resolve) => setTimeout(resolve, 500))
    tasks.value = getMockTasks(props.type, props.filters)
    totalPages.value = Math.ceil(tasks.value.length / 6)
  } catch (e) {
    error.value = 'Ошибка при загрузке заданий'
  } finally {
    isLoading.value = false
  }
})

// Вспомогательные функции
function generateDefaultParams() {
  const baseParams = {
    difficulty: props.filters.difficulty,
  }

  switch (props.type) {
    case 'word-translation':
    case 'word-matching':
      return {
        ...baseParams,
        word_type: props.filters.wordType,
      }
    case 'term-definition':
      return {
        ...baseParams,
        category: props.filters.category,
      }
    case 'chat-dialog':
    case 'email-structure':
      return {
        ...baseParams,
        terms: props.filters.selectedItems
          .filter((item) => item.type === 'term')
          .map((item) => item.value),
        words: props.filters.selectedItems
          .filter((item) => item.type === 'word')
          .map((item) => item.value),
      }
    default:
      return baseParams
  }
}

function getTaskTitle(type) {
  const titles = {
    'word-translation': 'Перевод слов',
    'word-matching': 'Сопоставление слов',
    'term-definition': 'Определение термина',
    'chat-dialog': 'Технический диалог',
    'email-structure': 'Структура email',
  }
  return titles[type] || 'Новое задание'
}

function getTaskDescription(data) {
  // TODO: Генерация описания на основе данных задания
  return 'Описание задания будет здесь'
}

// Моковые данные для примера
function getMockTasks(type, filters) {
  return Array(5)
    .fill(null)
    .map((_, index) => ({
      id: index + 1,
      title: getTaskTitle(type),
      description: `Тестовое задание #${index + 1}`,
      difficulty: filters.difficulty,
      progress: Math.floor(Math.random() * 100),
      extra: `Дополнительная информация для задания #${index + 1}`,
    }))
}
</script>
