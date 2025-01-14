<!-- src/components/tasks/TaskFilters.vue -->
<template>
  <div class="space-y-4">
    <!-- Типы заданий -->
    <div class="grid grid-cols-2 md:grid-cols-5 gap-2">
      <button
        v-for="type in taskTypes"
        :key="type.value"
        @click="$emit('update:selectedType', type.value)"
        class="p-2 rounded-lg text-sm text-center transition-colors"
        :class="[
          modelValue === type.value
            ? 'bg-light-accent dark:bg-dark-accent text-white'
            : 'bg-light-primary/10 dark:bg-dark-primary/10 hover:bg-light-primary/20 dark:hover:bg-dark-primary/20',
        ]"
      >
        {{ type.label }}
      </button>
    </div>

    <!-- Фильтры -->
    <div class="grid grid-cols-1 md:grid-cols-3 gap-4">
      <!-- Категория для терминов -->
      <div v-if="showCategoryFilter" class="space-y-2">
        <label class="text-sm font-medium">Категория</label>
        <select
          v-model="localFilters.category"
          class="w-full p-2 rounded-lg bg-light-primary/5 dark:bg-dark-primary/5 border border-light-primary/10 dark:border-dark-primary/10"
          @change="emitFilters"
        >
          <option value="">Все категории</option>
          <option v-for="cat in categories" :key="cat" :value="cat">
            {{ cat }}
          </option>
        </select>
      </div>

      <!-- Тип слова -->
      <div v-if="showWordTypeFilter" class="space-y-2">
        <label class="text-sm font-medium">Тип слова</label>
        <select
          v-model="localFilters.wordType"
          class="w-full p-2 rounded-lg bg-light-primary/5 dark:bg-dark-primary/5 border border-light-primary/10 dark:border-dark-primary/10"
          @change="emitFilters"
        >
          <option value="">Все типы</option>
          <option v-for="type in wordTypes" :key="type.value" :value="type.value">
            {{ type.label }}
          </option>
        </select>
      </div>

      <!-- Сложность -->
      <div class="space-y-2">
        <label class="text-sm font-medium">Сложность</label>
        <select
          v-model="localFilters.difficulty"
          class="w-full p-2 rounded-lg bg-light-primary/5 dark:bg-dark-primary/5 border border-light-primary/10 dark:border-dark-primary/10"
          @change="emitFilters"
        >
          <option v-for="diff in difficulties" :key="diff.value" :value="diff.value">
            {{ diff.label }}
          </option>
        </select>
      </div>
    </div>

    <!-- Выбор конкретных элементов -->
    <ItemSelector
      v-if="showItemSelector"
      v-model="localFilters.selectedItems"
      :type="modelValue"
      :category="localFilters.category"
      :word-type="localFilters.wordType"
      @update:modelValue="emitFilters"
    />
  </div>
</template>

<script setup>
import { ref, reactive, computed, watch } from 'vue'
import ItemSelector from './ItemSelector.vue'

const props = defineProps({
  modelValue: {
    type: String,
    required: true,
  },
  filters: {
    type: Object,
    required: true,
  },
})

const emit = defineEmits(['update:modelValue', 'update:filters'])

// Локальное состояние фильтров
const localFilters = reactive({ ...props.filters })

// Списки для фильтров
const taskTypes = [
  { value: 'word-translation', label: 'Перевод слов' },
  { value: 'word-matching', label: 'Сопоставление' },
  { value: 'term-definition', label: 'Определения' },
  { value: 'chat-dialog', label: 'Диалоги' },
  { value: 'email-structure', label: 'Email' },
]

const categories = ['backend', 'frontend', 'database', 'network'] // TODO: загрузка из API

const wordTypes = [
  { value: 'NOUN', label: 'Существительные' },
  { value: 'VERB', label: 'Глаголы' },
  { value: 'ADJECTIVE', label: 'Прилагательные' },
  { value: 'PHRASAL_VERB', label: 'Фразовые глаголы' },
]

const difficulties = [
  { value: 'basic', label: 'Базовый' },
  { value: 'intermediate', label: 'Средний' },
  { value: 'advanced', label: 'Продвинутый' },
]

// Вычисляемые свойства для отображения фильтров
const showCategoryFilter = computed(() =>
  ['term-definition', 'chat-dialog', 'email-structure'].includes(props.modelValue),
)

const showWordTypeFilter = computed(() =>
  ['word-translation', 'word-matching'].includes(props.modelValue),
)

const showItemSelector = computed(() =>
  ['chat-dialog', 'email-structure'].includes(props.modelValue),
)

// Методы
function emitFilters() {
  emit('update:filters', { ...localFilters })
}

// Следим за изменениями внешних фильтров
watch(
  () => props.filters,
  (newFilters) => {
    Object.assign(localFilters, newFilters)
  },
  { deep: true },
)
</script>
