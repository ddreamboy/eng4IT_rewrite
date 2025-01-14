<template>
  <div class="p-6">
    <h1 class="text-2xl font-bold mb-4">Термины и Слова</h1>
    <input
      v-model="searchQuery"
      type="text"
      placeholder="Поиск..."
      class="w-full mb-4 p-2 border rounded"
    />

    <!-- Фильтры и пагинация -->
    <div class="flex justify-between items-center mb-4">
      <div>
        <button
          @click="filterType = 'all'"
          :class="{'bg-blue-500 text-white': filterType === 'all'}"
          class="px-3 py-1 rounded mr-2"
        >
          Все
        </button>
        <button
          @click="filterType = 'terms'"
          :class="{'bg-blue-500 text-white': filterType === 'terms'}"
          class="px-3 py-1 rounded mr-2"
        >
          Термины
        </button>
        <button
          @click="filterType = 'words'"
          :class="{'bg-blue-500 text-white': filterType === 'words'}"
          class="px-3 py-1 rounded"
        >
          Слова
        </button>
      </div>
      <div>
        <button @click="prevPage" :disabled="currentPage === 1" class="px-3 py-1 rounded mr-2">
          Назад
        </button>
        <span>Страница {{ currentPage }}</span>
        <button @click="nextPage" :disabled="!hasMore" class="px-3 py-1 rounded ml-2">
          Вперед
        </button>
      </div>
    </div>

    <!-- Список терминов и слов с фильтрацией -->
    <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
      <div
        v-for="item in paginatedItems"
        :key="item.id"
        class="p-4 bg-light-secondary dark:bg-dark-secondary rounded relative"
      >
        <div @click="openModal(item)" class="cursor-pointer">
          <!-- Термин -->
          <h2 v-if="item.term" class="text-xl font-semibold">{{ item.term }}</h2>
          <!-- Слово -->
          <h2 v-else class="text-xl font-semibold">{{ item.word }}</h2>

          <!-- Перевод -->
          <p v-if="item.primary_translation" class="text-gray-600">
            {{ item.primary_translation }}
          </p>
          <p v-else class="text-gray-600">
            {{ item.translation }}
          </p>

          <!-- Дополнительные поля для терминов -->
          <div v-if="item.category_main">
            <p><strong>Категория:</strong> {{ item.category_main }}<span v-if="item.category_sub"> / {{ item.category_sub }}</span></p>
          </div>

          <!-- Значки избранного и звука -->
          <div class="absolute top-2 right-2 flex space-x-2">
            <button @click.stop="toggleFavorite(item)" class="focus:outline-none">
              <svg v-if="isFavorite(item)" xmlns="http://www.w3.org/2000/svg" class="h-6 w-6 text-yellow-500" fill="currentColor" viewBox="0 0 24 24">
                <!-- Заполненная звезда -->
                <path d="M12 17.27L18.18 21l-1.64-7.03L22 9.24l-7.19-.61L12 2 9.19 8.63 2 9.24l5.46 4.73L5.82 21z"/>
              </svg>
              <svg v-else xmlns="http://www.w3.org/2000/svg" class="h-6 w-6 text-gray-400" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <!-- Пустая звезда -->
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M11.049 2.927c.3-.921 1.603-.921 1.902 0l2.18 6.725a1 1 0 00.95.69h7.072c.969 0 1.371 1.24.588 1.81l-5.734 4.165a1 1 0 00-.364 1.118l2.18 6.725c.3.921-.755 1.688-1.54 1.118l-5.734-4.165a1 1 0 00-1.176 0l-5.734 4.165c-.784.57-1.838-.197-1.54-1.118l2.18-6.725a1 1 0 00-.364-1.118l-5.734-4.165c-.783-.57-.38-1.81.588-1.81h7.072a1 1 0 00.95-.69l2.18-6.725z" />
              </svg>
            </button>
            <button @click.stop="playAudio(item)" class="focus:outline-none">
              <svg xmlns="http://www.w3.org/2000/svg" class="h-6 w-6 text-blue-500" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <!-- Иконка звука -->
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 10l4.553-2.276A1 1 0 0121 8.618v6.764a1 1 0 01-1.447.894L15 14m-6 0v-4l-4-2m0 8V6m0 0L5.447 8.276A1 1 0 015 8.618v6.764a1 1 0 001.447.894L9 14m0 0v4l4 2" />
              </svg>
            </button>
          </div>
        </div>
      </div>
    </div>

    <!-- Модальное окно -->
    <div v-if="isModalOpen" class="fixed inset-0 flex items-center justify-center bg-black bg-opacity-50">
      <div class="bg-white dark:bg-gray-800 p-6 rounded-lg relative w-11/12 md:w-1/2">
        <button @click="isModalOpen = false" class="absolute top-2 right-2 text-gray-500">
          <!-- Иконка закрытия -->
          <svg xmlns="http://www.w3.org/2000/svg" class="h-6 w-6" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12" />
          </svg>
        </button>

        <div v-if="selectedItem">
          <!-- Информация для терминов -->
          <div v-if="selectedItem.term">
            <h2 class="text-2xl font-bold mb-2">{{ selectedItem.term }}</h2>
            <p><strong>Категория:</strong> {{ selectedItem.category_main }}<span v-if="selectedItem.category_sub"> / {{ selectedItem.category_sub }}</span></p>
            <p><strong>Определение (EN):</strong> {{ selectedItem.definition_en }}</p>
            <p><strong>Определение (RU):</strong> {{ selectedItem.definition_ru }}</p>
          </div>
          <!-- Информация для слов -->
          <div v-else>
            <h2 class="text-2xl font-bold mb-2">{{ selectedItem.word }}</h2>
            <p class="text-gray-600">{{ selectedItem.translation }}</p>
            <p><strong>Тип слова:</strong> {{ selectedItem.word_type }}</p>
            <p><strong>Сложность:</strong> {{ selectedItem.difficulty }}</p>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted, computed, watch } from 'vue'
import axios from 'axios'
import debounce from 'lodash/debounce'

// Состояние для терминов и слов
const terms = ref([])
const words = ref([])
const searchQuery = ref('')

// Фильтрация и пагинация
const filterType = ref('all') // 'all', 'terms', 'words'
const currentPage = ref(1)
const itemsPerPage = 10
const hasMore = ref(true)

// Избранное
const favorites = ref([])

// Модальное окно
const isModalOpen = ref(false)
const selectedItem = ref(null)

// Функция для загрузки данных с сервера
const fetchData = async () => {
  try {
    const [termsResponse, wordsResponse] = await Promise.all([
      axios.get('/api/v1/terms', { params: { page: currentPage.value, page_size: itemsPerPage } }),
      axios.get('/api/v1/words', { params: { page: currentPage.value, page_size: itemsPerPage } }),
    ])
    terms.value = termsResponse.data
    words.value = wordsResponse.data
    hasMore.value = terms.value.length === itemsPerPage || words.value.length === itemsPerPage
  } catch (error) {
    console.error('Ошибка при загрузке данных:', error)
  }
}

// Фильтрация данных на основе запроса поиска и типа
const filteredTerms = computed(() => {
  if (filterType.value === 'words') return []
  let data = terms.value
  if (filterType.value === 'terms' || filterType.value === 'all') {
    if (searchQuery.value) {
      const query = searchQuery.value.toLowerCase()
      data = data.filter(term =>
        term.term.toLowerCase().includes(query) ||
        term.primary_translation.toLowerCase().includes(query)
      )
    }
  }
  return data
})

const filteredWords = computed(() => {
  if (filterType.value === 'terms') return []
  let data = words.value
  if (filterType.value === 'words' || filterType.value === 'all') {
    if (searchQuery.value) {
      const query = searchQuery.value.toLowerCase()
      data = data.filter(word =>
        word.word.toLowerCase().includes(query) ||
        word.translation.toLowerCase().includes(query)
      )
    }
  }
  return data
})

// Пагинация
const paginatedItems = computed(() => {
  if (filterType.value === 'terms') return filteredTerms.value
  if (filterType.value === 'words') return filteredWords.value
  return [...filteredTerms.value, ...filteredWords.value]
})

// Обновление флага hasMore на основе полученных данных
watch([filteredTerms, filteredWords, currentPage], () => {
  hasMore.value = terms.value.length === itemsPerPage || words.value.length === itemsPerPage
})

onMounted(() => {
  fetchData()
})

// Обновление данных при изменении поискового запроса с задержкой
watch(searchQuery, debounce(() => {
  currentPage.value = 1
  fetchData()
}, 300))

function nextPage() {
  if (hasMore.value) {
    currentPage.value += 1
    fetchData()
  }
}

function prevPage() {
  if (currentPage.value > 1) {
    currentPage.value -= 1
    fetchData()
  }
}

// Избранное
const toggleFavorite = async (item) => {
  try {
    const endpoint = item.term ? `/api/v1/terms/favorite/${item.id}` : `/api/v1/words/favorite/${item.id}`
    const response = await axios.post(endpoint, { state: !isFavorite(item) }, {
      headers: { Authorization: `Bearer ${localStorage.getItem('token')}` }
    })
    if (response.data.message) {
      if (isFavorite(item)) {
        favorites.value = favorites.value.filter(id => id !== item.id)
      } else {
        favorites.value.push(item.id)
      }
    }
  } catch (error) {
    console.error('Ошибка при добавлении в избранное:', error)
  }
}

const isFavorite = (item) => {
  return favorites.value.includes(item.id)
}

// Воспроизведение аудио
const playAudio = (item) => {
  const endpoint = item.term ? `/api/v1/audio/terms/${item.id}` : `/api/v1/audio/words/${item.id}`
  const audio = new Audio(endpoint)
  audio.play().catch(error => console.error('Ошибка воспроизведения аудио:', error))
}

// Модальное окно
const openModal = (item) => {
  selectedItem.value = item
  isModalOpen.value = true
}
</script>

<style scoped>

</style>