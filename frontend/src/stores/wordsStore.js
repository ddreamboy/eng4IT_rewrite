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
    total: 0
  })
  const filters = ref({
    difficulty: null,
    wordType: null,
    search: ''
  })
  const favorites = ref([])

  // Actions
  async function fetchWords() {
    loading.value = true
    error.value = null

    try {
      const response = await axios.get(`${API_URL}/words/`, {
        params: {
          page: pagination.value.page,
          page_size: pagination.value.pageSize,
          difficulty: filters.value.difficulty,
          word_type: filters.value.wordType,
          search: filters.value.search
        }
      })

      words.value = response.data
    } catch (err) {
      error.value = err.response?.data?.detail || 'Не удалось загрузить слова'
      console.error('Words fetch error:', err)
    } finally {
      loading.value = false
    }
  }

  async function toggleFavorite(wordId) {
    try {
      const currentState = await checkFavoriteStatus(wordId)
      
      await axios.post(`${API_URL}/words/favorite`, null, {
        params: {
          word_id: wordId,
          state: !currentState
        }
      })

      // Обновляем локальный список избранных
      if (currentState) {
        favorites.value = favorites.value.filter(id => id !== wordId)
      } else {
        favorites.value.push(wordId)
      }
    } catch (err) {
      console.error('Toggle favorite error:', err)
    }
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
        responseType: 'blob'
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
      search: ''
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
    checkFavoriteStatus,
    fetchWordAudio,
    resetFilters
  }
})