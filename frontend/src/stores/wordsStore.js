// src/stores/wordsStore.js
import { defineStore } from 'pinia'
import { ref } from 'vue'
import axios from 'axios'

const API_URL = import.meta.env.VITE_API_URL || 'http://localhost:7000/api/v1'

export const useWordsStore = defineStore('words', () => {
  // State
  const words = ref([])
  const loading = ref(false)
  const error = ref(null)
  const pagination = ref({
    page: 1,
    pageSize: 10,
    total: 0,
  })
  const filters = ref({
    difficulty: null,
    wordType: null,
    search: '',
  })
  const favorites = ref([])

  // Actions
  async function fetchWords(params = {}) {
    loading.value = true
    error.value = null
  
    try {
      const response = await axios.get(`${API_URL}/words/`, {
        params: {
          page: params.page || pagination.value.page,
          page_size: params.page_size || pagination.value.pageSize,
          difficulty: params.difficulty,
          search: params.search,
          favorites_only: params.favorites_only
        },
      })
  
      // Обновляем состояние store в соответствии с форматом API
      words.value = response.data.items
      pagination.value = {
        page: response.data.page,
        pageSize: response.data.page_size,
        total: response.data.total,
        totalPages: response.data.total_pages
      }
    } catch (err) {
      error.value = err.response?.data?.detail || 'Не удалось загрузить слова'
      console.error('Words fetch error:', err)
    } finally {
      loading.value = false
    }
  }

  async function toggleFavorite(itemId) {
    try {
      const currentState = await checkFavoriteStatus(itemId)

      const response = await axios.post(`${API_URL}/words/favorite`, null, {
        params: {
          word_id: itemId,
          state: !currentState,
        },
      })

      if (!currentState) {
        favorites.value.push(itemId)
      } else {
        favorites.value = favorites.value.filter((id) => id !== itemId)
      }

      return !currentState
    } catch (err) {
      console.error('Toggle favorite error:', err)
      throw err
    }
  }

  async function fetchFavorites() {
    const promises = words.value.map((word) => checkFavoriteStatus(word.id))
    const statuses = await Promise.all(promises)
    favorites.value = words.value.filter((_, index) => statuses[index]).map((word) => word.id)
  }

  async function checkFavoriteStatus(wordId) {
    try {
      const response = await axios.get(`${API_URL}/words/favorite/${wordId}`)
      return response.data.is_favorite
    } catch (err) {
      console.error('Favorite status check error:', err)
      return false
    }
  }

  async function fetchWordAudio(wordId) {
    try {
      const response = await axios.get(`${API_URL}/audio/words/${wordId}`, {
        responseType: 'blob',
      })

      // Создаем URL для воспроизведения аудио
      const audioUrl = URL.createObjectURL(response.data)
      const audio = new Audio(audioUrl)
      audio.play()

      return audioUrl
    } catch (err) {
      console.error('Word audio fetch error:', err)
      return null
    }
  }

  // Сбрасываем фильтры
  function resetFilters() {
    filters.value = {
      difficulty: null,
      wordType: null,
      search: '',
    }
    pagination.value.page = 1
    fetchWords()
  }

  return {
    words,
    loading,
    error,
    pagination,
    filters,
    favorites,
    fetchWords,
    toggleFavorite,
    fetchFavorites,
    checkFavoriteStatus,
    fetchWordAudio,
    resetFilters,
  }
})
