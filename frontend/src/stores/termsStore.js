// src/stores/termsStore.js
import { defineStore } from 'pinia'
import { ref } from 'vue'
import axios from 'axios'

const API_URL = import.meta.env.VITE_API_URL || 'http://localhost:7000/api/v1'

export const useTermsStore = defineStore('terms', () => {
  // State
  const terms = ref([])
  const loading = ref(false)
  const error = ref(null)
  const pagination = ref({
    page: 1,
    pageSize: 10,
    total: 0,
  })
  const filters = ref({
    difficulty: null,
    category: null,
    search: '',
  })
  const favorites = ref([])

  // Actions
  async function fetchTerms() {
    loading.value = true
    error.value = null

    try {
      const response = await axios.get(`${API_URL}/terms/`, {
        params: {
          page: pagination.value.page,
          page_size: pagination.value.pageSize,
          difficulty: filters.value.difficulty,
          category: filters.value.category,
          search: filters.value.search,
        },
      })

      terms.value = response.data
      // Предполагаем, что сервер возвращает общее количество в headers или meta
      // pagination.value.total = response.headers['x-total-count'] || response.data.total
    } catch (err) {
      error.value = err.response?.data?.detail || 'Не удалось загрузить термины'
      console.error('Terms fetch error:', err)
    } finally {
      loading.value = false
    }
  }

  async function toggleFavorite(itemId) {
    try {
      // Получаем текущий статус
      const currentState = await checkFavoriteStatus(itemId)

      // Отправляем запрос на сервер
      await axios.post(`${API_URL}/terms/favorite`, null, {
        params: {
          term_id: itemId,
          state: !currentState,
        },
      })

      // Обновляем локальный список избранных
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
    const promises = terms.value.map((term) => checkFavoriteStatus(term.id))
    const statuses = await Promise.all(promises)
    favorites.value = terms.value.filter((_, index) => statuses[index]).map((term) => term.id)
  }

  async function checkFavoriteStatus(termId) {
    try {
      const response = await axios.get(`${API_URL}/terms/favorite/${termId}`)
      return response.data.is_favorite
    } catch (err) {
      console.error('Favorite status check error:', err)
      return false
    }
  }

  async function fetchTermAudio(termId) {
    try {
      const response = await axios.get(`${API_URL}/audio/terms/${termId}`, {
        responseType: 'blob',
      })

      // Создаем URL для воспроизведения аудио
      const audioUrl = URL.createObjectURL(response.data)
      const audio = new Audio(audioUrl)
      audio.play()

      return audioUrl
    } catch (err) {
      console.error('Term audio fetch error:', err)
      return null
    }
  }

  // Сбрасываем фильтры
  function resetFilters() {
    filters.value = {
      difficulty: null,
      category: null,
      search: '',
    }
    pagination.value.page = 1
    fetchTerms()
  }

  return {
    terms,
    loading,
    error,
    pagination,
    filters,
    favorites,
    fetchTerms,
    toggleFavorite,
    fetchFavorites,
    checkFavoriteStatus,
    fetchTermAudio,
    resetFilters,
  }
})
