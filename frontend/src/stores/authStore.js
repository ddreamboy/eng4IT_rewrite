// Path: src/stores/authStore.js
import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import axios from 'axios'

const API_URL = import.meta.env.VITE_API_URL || 'http://localhost:7000/api/v1'

export const useAuthStore = defineStore('auth', () => {
  const user = ref(null)
  const token = ref(localStorage.getItem('token'))
  
  // Проверяем валидность токена при инициализации
  if (token.value && !isTokenValid(token.value)) {
    token.value = null
    localStorage.removeItem('token')
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

  function setAuthHeader() {
    if (token.value) {
      axios.defaults.headers.common['Authorization'] = `Bearer ${token.value}`
    } else {
      delete axios.defaults.headers.common['Authorization']
    }
  }

  // Инициализация
  setAuthHeader()

  async function register(credentials) {
    try {
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
      formData.append('username', credentials.username)
      formData.append('password', credentials.password)
      formData.append('grant_type', 'password')
      formData.append('scope', '')
      formData.append('client_id', '')
      formData.append('client_secret', '')
  
      const response = await axios.post(`${API_URL}/auth/login`, formData, {
        headers: {
          'Content-Type': 'application/x-www-form-urlencoded'
        }
      })
  
      if (!response?.data?.access_token) {
        throw new Error('Invalid server response - no token received')
      }
  
      token.value = response.data.access_token
      localStorage.setItem('token', response.data.access_token)
      
      setAuthHeader()
  
      const tokenData = JSON.parse(atob(response.data.access_token.split('.')[1]))
      user.value = {
        id: tokenData.sub,
        username: tokenData.username || tokenData.email
      }
  
      return true
    } catch (error) {
      console.error('Login error:', error)
      throw error
    }
  }

  function logout() {
    user.value = null
    token.value = null
    localStorage.removeItem('token')
    setAuthHeader()
  }

  return {
    user,
    token,
    isAuthenticated,
    userInitials,
    register,
    login,
    logout,
  }
})