<!-- src/views/TasksPage.vue -->
<template>
  <div class="space-y-6">
    <!-- Шапка и управление -->
    <div class="flex justify-between items-center">
      <h1 class="text-2xl font-bold">Задания</h1>

      <!-- Переключатель режима разработчика -->
      <button
        v-if="isDevelopment"
        @click="isDevMode = !isDevMode"
        class="px-3 py-1.5 text-sm rounded-lg"
        :class="
          isDevMode
            ? 'bg-light-accent dark:bg-dark-accent text-white'
            : 'bg-light-primary/10 dark:bg-dark-primary/10'
        "
      >
        {{ isDevMode ? 'Обычный режим' : 'Режим разработчика' }}
      </button>
    </div>

    <!-- Фильтры -->
    <TaskFilters
      v-model:selectedType="selectedType"
      v-model:filters="filters"
      @update:filters="updateFilters"
    />

    <!-- Режим разработчика -->
    <DevModePanel
      v-if="isDevMode"
      v-model:params="customParams"
      :selectedType="selectedType"
      @generate="generateTask"
    />

    <!-- Список заданий -->
    <TaskList
      :type="selectedType"
      :filters="filters"
      :custom-params="isDevMode ? customParams : null"
      @select="selectTask"
    />
  </div>
</template>

<script setup>
import { ref, reactive } from 'vue'
import TaskFilters from '../components/tasks/TaskFilters.vue'
import TaskList from '../components/tasks/TaskList.vue'
import DevModePanel from '../components/tasks/DevModePanel.vue'

// Режим разработчика (только в dev)
const isDevMode = ref(false)
const customParams = ref({})

// Добавлено: Переменная для определения режима разработки
const isDevelopment = import.meta.env.DEV

// Фильтры и выбранный тип
const selectedType = ref('word-translation')
const filters = reactive({
  category: null,
  wordType: null,
  selectedItems: [],
  difficulty: 'intermediate',
})

function updateFilters(newFilters) {
  Object.assign(filters, newFilters)
}

function selectTask(task) {
  // TODO: Обработка выбора задания
  console.log('Selected task:', task)
}

function generateTask(params) {
  // TODO: Генерация задания с параметрами
  console.log('Generating task with params:', params)
}
</script>
