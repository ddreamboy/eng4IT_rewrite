<!-- src/views/TermsWordsPage.vue -->
<template>
  <div class="container mx-auto px-4 py-8">
    <!-- Переключатель вкладок -->
    <div
      class="flex mb-6 rounded-lg overflow-hidden"
      :class="[themeStore.isDark ? 'bg-dark-primary' : 'bg-light-primary']"
    >
      <button
        @click="activeTab = 'terms'"
        class="flex-1 py-2 transition-colors"
        :class="[
          activeTab === 'terms'
            ? [
                themeStore.isDark
                  ? 'bg-dark-accent text-dark-text'
                  : 'bg-light-accent text-light-text',
              ]
            : [
                themeStore.isDark
                  ? 'text-dark-text/50 hover:bg-dark-primary/50'
                  : 'text-light-text/50 hover:bg-light-primary/50',
              ],
        ]"
      >
        Термины
      </button>
      <button
        @click="activeTab = 'words'"
        class="flex-1 py-2 transition-colors"
        :class="[
          activeTab === 'words'
            ? [
                themeStore.isDark
                  ? 'bg-dark-accent text-dark-text'
                  : 'bg-light-accent text-light-text',
              ]
            : [
                themeStore.isDark
                  ? 'text-dark-text/50 hover:bg-dark-primary/50'
                  : 'text-light-text/50 hover:bg-light-primary/50',
              ],
        ]"
      >
        Слова
      </button>
    </div>

    <!-- Фильтры -->
    <div class="mb-6 flex space-x-4">
      <!-- Фильтр сложности -->
      <select
        v-model="currentFilters.difficulty"
        @change="applyFilters"
        class="px-4 py-2 rounded-lg transition-colors"
        :class="[
          themeStore.isDark
            ? 'bg-dark-secondary text-dark-text border-dark-primary'
            : 'bg-light-secondary text-light-text border-light-primary',
        ]"
      >
        <option value="">Уровень</option>
        <option value="beginner">Начинающий</option>
        <option value="basic">Базовый</option>
        <option value="intermediate">Средний</option>
        <option value="advanced">Сложный</option>
      </select>

      <!-- Поиск -->
      <div class="flex-grow relative">
        <input
          v-model="currentFilters.search"
          @input="debouncedApplyFilters"
          placeholder="Поиск..."
          class="w-full px-4 py-2 rounded-lg transition-colors"
          :class="[
            themeStore.isDark
              ? 'bg-dark-secondary text-dark-text border-dark-primary'
              : 'bg-light-secondary text-light-text border-light-primary',
          ]"
        />
      </div>

      <!-- Сброс фильтров -->
      <button
        @click="resetFilters"
        class="px-4 py-2 rounded-lg transition-colors"
        :class="[
          themeStore.isDark
            ? 'bg-dark-accent text-dark-text hover:bg-dark-accent/90'
            : 'bg-light-accent text-light-text hover:bg-light-accent/90',
        ]"
      >
        Сбросить
      </button>
    </div>

    <!-- Лоадер -->
    <div v-if="loading" class="flex justify-center items-center py-12">
      <div
        class="animate-spin rounded-full h-8 w-8 border-b-2"
        :class="[themeStore.isDark ? 'border-dark-accent' : 'border-light-accent']"
      ></div>
    </div>

    <!-- Сетка с контентом -->
    <div
      v-else-if="displayItems.length"
      class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6"
    >
      <TermCard
        v-if="activeTab === 'terms'"
        v-for="term in displayItems"
        :key="term.id"
        :term="term"
      />
      <WordCard v-else v-for="word in displayItems" :key="word.id" :word="word" />
    </div>

    <!-- Пустой стейт -->
    <div
      v-else
      class="text-center py-12"
      :class="[themeStore.isDark ? 'text-dark-text/50' : 'text-light-text/50']"
    >
      Ничего не найдено
    </div>

    <!-- Пагинация -->
    <div v-if="displayItems.length" class="flex justify-center mt-8 space-x-4">
      <button
        @click="prevPage"
        :disabled="currentPage === 1"
        class="px-4 py-2 rounded-lg transition-colors disabled:opacity-50"
        :class="[
          themeStore.isDark
            ? 'bg-dark-accent text-dark-text hover:bg-dark-accent/90'
            : 'bg-light-accent text-light-text hover:bg-light-accent/90',
        ]"
      >
        Назад
      </button>
      <span class="px-4 py-2" :class="[themeStore.isDark ? 'text-dark-text' : 'text-light-text']">
        Страница {{ currentPage }}
      </span>
      <button
        @click="nextPage"
        :disabled="!hasMorePages"
        class="px-4 py-2 rounded-lg transition-colors disabled:opacity-50"
        :class="[
          themeStore.isDark
            ? 'bg-dark-accent text-dark-text hover:bg-dark-accent/90'
            : 'bg-light-accent text-light-text hover:bg-light-accent/90',
        ]"
      >
        Вперед
      </button>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, watch } from 'vue'
import { useThemeStore } from '@/stores/themeStore'
import { useTermsStore } from '@/stores/termsStore'
import { useWordsStore } from '@/stores/wordsStore'
import TermCard from '@/components/TermCard.vue'
import WordCard from '@/components/WordCard.vue'
import { debounce } from 'lodash'

// Stores
const themeStore = useThemeStore()
const termsStore = useTermsStore()
const wordsStore = useWordsStore()

// Активная вкладка
const activeTab = ref('terms')

// Текущая страница и фильтры
const currentPage = ref(1)
const currentFilters = ref({
  difficulty: '',
  search: '',
})

// Состояние загрузки
const loading = ref(false)

// Вычисляемые свойства
const displayItems = computed(() => {
  // Добавляем проверку на пустые данные
  const items = activeTab.value === 'terms' ? termsStore.terms : wordsStore.words
  console.log('Display items:', items) // Для отладки
  return items || []
})

const hasMorePages = computed(() => {
  const store = activeTab.value === 'terms' ? termsStore : wordsStore
  // Предполагаем, что если получено полное количество элементов, есть еще страницы
  return displayItems.value.length === store.pagination.pageSize
})

// Методы навигации
function prevPage() {
  if (currentPage.value > 1) {
    currentPage.value--
    fetchCurrentItems()
  }
}

function nextPage() {
  if (hasMorePages.value) {
    currentPage.value++
    fetchCurrentItems()
  }
}

// Применение фильтров
function applyFilters() {
  currentPage.value = 1
  fetchCurrentItems()
}

// Отложенное применение фильтров для поиска
const debouncedApplyFilters = debounce(applyFilters, 500)

// Сброс фильтров
function resetFilters() {
  currentFilters.value = {
    difficulty: '',
    search: '',
  }
  currentPage.value = 1
  fetchCurrentItems()
}

// Загрузка элементов
async function fetchCurrentItems() {
  loading.value = true

  try {
    if (activeTab.value === 'terms') {
      termsStore.filters.difficulty = currentFilters.value.difficulty
      termsStore.filters.search = currentFilters.value.search
      termsStore.pagination.page = currentPage.value
      await termsStore.fetchTerms()
      await termsStore.fetchFavorites() // Добавляем загрузку избранных
    } else {
      wordsStore.filters.difficulty = currentFilters.value.difficulty
      wordsStore.filters.search = currentFilters.value.search
      wordsStore.pagination.page = currentPage.value
      await wordsStore.fetchWords()
      await wordsStore.fetchFavorites() // Добавляем загрузку избранных
    }
  } catch (error) {
    console.error('Ошибка загрузки:', error)
  } finally {
    loading.value = false
  }
}

// Следим за изменением вкладки
watch(activeTab, () => {
  currentPage.value = 1
  currentFilters.value = {
    difficulty: '',
    search: '',
  }
  fetchCurrentItems()
})

// Инициализация при монтировании
onMounted(() => {
  fetchCurrentItems()
})
</script>
