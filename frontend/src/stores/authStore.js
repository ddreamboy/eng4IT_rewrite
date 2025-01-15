// src/stores/authStore.js
import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import axios from 'axios'

const API_URL = import.meta.env.VITE_API_URL || 'http://localhost:7000/api/v1'

export const useAuthStore = defineStore('auth', () => {
  const user = ref(null)
  const token = ref(localStorage.getItem('token'))
  const refreshToken = ref(localStorage.getItem('refreshToken'))
  console.log('Initial token:', token.value)

  if (token.value && !isTokenValid(token.value)) {
    token.value = null
    refreshToken.value = null
    localStorage.removeItem('token')
    localStorage.removeItem('refreshToken')
  }

  const isAuthenticated = computed(() => {
    if (!token.value) return false
    return isTokenValid(token.value)
  })
  const userInitials = computed(() => {
    if (!user.value?.username) return '?'
    return user.value.username
      .split(' ')
      .map((n) => n[0])
      .join('')
      .toUpperCase()
  })

  function isTokenValid(token) {
    if (!token) return false
    try {
      const tokenData = JSON.parse(atob(token.split('.')[1]))
      return tokenData.exp * 1000 > Date.now()
    } catch (e) {
      return false
    }
  }

  // Настройка axios с токеном
  function setAuthHeader() {
    if (token.value) {
      axios.defaults.headers.common['Authorization'] = `Bearer ${token.value}`
    } else {
      delete axios.defaults.headers.common['Authorization']
    }
  }

  // Добавить функцию для извлечения данных пользователя из токена
  function setUserFromToken() {
    if (token.value) {
      const tokenPayload = JSON.parse(atob(token.value.split('.')[1]))
      user.value = {
        id: tokenPayload.sub,
        username: tokenPayload.username || tokenPayload.email, // Используем username или email из токена
      }
    }
  }

  // Инициализация при создании стора
  setAuthHeader()
  setUserFromToken()

  // Обработка 401 ошибки и обновление токена
  axios.interceptors.response.use(
    (response) => response,
    async (error) => {
      const originalRequest = error.config
      if (error.response.status === 401 && !originalRequest._retry) {
        originalRequest._retry = true
        try {
          await refreshTokens()
          return axios(originalRequest)
        } catch (refreshError) {
          logout()
          throw refreshError
        }
      }
      return Promise.reject(error)
    },
  )

  async function register(credentials) {
    try {
      // Отправляем данные как JSON объект напрямую
      const response = await axios.post(`${API_URL}/auth/register`, {
        username: credentials.username,
        email: credentials.email,
        password: credentials.password
      }, {
        headers: {
          'Content-Type': 'application/json'
        }
      })
  
      return response.data
    } catch (error) {
      console.error('Register error:', error)
      throw error
    }
  }

  async function login(credentials) {
    try {
      const formData = new URLSearchParams()
      formData.append('grant_type', 'password')
      formData.append('username', credentials.username)
      formData.append('password', credentials.password)
      formData.append('scope', '')
      formData.append('client_id', '')
      formData.append('client_secret', '')

      const response = await axios.post(`${API_URL}/auth/login`, formData, {
        headers: {
          'Content-Type': 'application/x-www-form-urlencoded',
        },
      })

      // Сохраняем токены
      token.value = response.data.access_token
      refreshToken.value = response.data.refresh_token
      localStorage.setItem('token', response.data.access_token)
      localStorage.setItem('refreshToken', response.data.refresh_token)

      // Обновляем заголовок для будущих запросов
      setAuthHeader()

      // Получаем информацию из токена
      const tokenData = JSON.parse(atob(response.data.access_token.split('.')[1]))
      user.value = {
        id: tokenData.sub,
        username: tokenData.username || credentials.email, // Изменено для использования данных из токена
      }

      return true
    } catch (error) {
      if (error.response) {
        console.error('Login error:', error.response.data)
        throw error
      } else {
        console.error('Login error:', error.message)
        throw error
      }
    }
  }

  async function refreshTokens() {
    try {
      console.log('Refreshing tokens, current token:', token.value)
      // Обрати внимание - здесь не нужно передавать refresh_token в теле запроса
      // Достаточно только Bearer token в заголовке
      const response = await axios.post(
        `${API_URL}/auth/refresh`,
        {}, // пустое тело запроса
        {
          headers: { 
            Authorization: `Bearer ${token.value}`,
            accept: 'application/json'
          },
        }
      )
      console.log('Refresh response:', response.data)
      
      // Обновляем токены из ответа
      token.value = response.data.access_token
      refreshToken.value = response.data.refresh_token
      localStorage.setItem('token', response.data.access_token)
      localStorage.setItem('refreshToken', response.data.refresh_token)
      setAuthHeader()
      return true
    } catch (error) {
      console.error('Token refresh error:', error)
      throw error
    }
  }

  function logout() {
    user.value = null
    token.value = null
    refreshToken.value = null
    localStorage.removeItem('token')
    localStorage.removeItem('refreshToken')
    setAuthHeader()
  }

  return {
    user,
    token,
    refreshToken,
    isAuthenticated,
    userInitials,
    register,
    login,
    refreshTokens,
    logout,
  }
})