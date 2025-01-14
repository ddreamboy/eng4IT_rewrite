<!-- src/views/AuthPage.vue -->
<template>
  <div class="min-h-[calc(100vh-4rem)] flex items-center justify-center">
    <div
      class="w-full max-w-md p-6 m-4 rounded-lg shadow-lg bg-light-secondary dark:bg-dark-secondary"
    >
      <!-- Переключатель форм -->
      <div class="flex p-1 mb-6 rounded-lg bg-light-primary/10 dark:bg-dark-primary/10">
        <button
          v-for="tab in ['login', 'register']"
          :key="tab"
          @click="activeTab = tab"
          class="flex-1 py-2 text-center rounded-md transition-colors"
          :class="
            activeTab === tab
              ? 'bg-light-accent dark:bg-dark-accent text-white'
              : 'hover:bg-light-primary/5 dark:hover:bg-dark-primary/5'
          "
        >
          {{ tab === 'login' ? 'Вход' : 'Регистрация' }}
        </button>
      </div>

      <!-- Форма авторизации -->
      <form @submit.prevent="handleSubmit" class="space-y-4">
        <!-- Username для регистрации -->
        <div v-if="activeTab === 'register'">
          <label class="block mb-1 text-sm">Имя пользователя</label>
          <input
            v-model="form.username"
            type="text"
            class="w-full px-4 py-2 rounded bg-light-primary/5 dark:bg-dark-primary/5 border border-light-primary/10 dark:border-dark-primary/10 focus:ring-2 focus:ring-light-accent dark:focus:ring-dark-accent"
            :class="{ 'border-red-500': errors.username }"
            placeholder="john_doe"
          />
          <p v-if="errors.username" class="mt-1 text-sm text-red-500">
            {{ errors.username }}
          </p>
        </div>

        <!-- Email -->
        <div>
          <label class="block mb-1 text-sm">Email</label>
          <input
            v-model="form.email"
            type="email"
            class="w-full px-4 py-2 rounded bg-light-primary/5 dark:bg-dark-primary/5 border border-light-primary/10 dark:border-dark-primary/10 focus:ring-2 focus:ring-light-accent dark:focus:ring-dark-accent"
            :class="{ 'border-red-500': errors.email }"
            placeholder="user@example.com"
          />
          <p v-if="errors.email" class="mt-1 text-sm text-red-500">
            {{ errors.email }}
          </p>
        </div>

        <!-- Password -->
        <div>
          <label class="block mb-1 text-sm">Пароль</label>
          <input
            v-model="form.password"
            type="password"
            class="w-full px-4 py-2 rounded bg-light-primary/5 dark:bg-dark-primary/5 border border-light-primary/10 dark:border-dark-primary/10 focus:ring-2 focus:ring-light-accent dark:focus:ring-dark-accent"
            :class="{ 'border-red-500': errors.password }"
            placeholder="password"
          />
          <p v-if="errors.password" class="mt-1 text-sm text-red-500">
            {{ errors.password }}
          </p>
        </div>

        <!-- Кнопка отправки -->
        <button
          type="submit"
          class="w-full py-2 text-white rounded-lg bg-light-accent dark:bg-dark-accent hover:opacity-90 transition-opacity"
          :disabled="isLoading"
        >
          <span v-if="isLoading">
            <LoaderIcon class="inline w-4 h-4 mr-2 animate-spin" />
            {{ activeTab === 'login' ? 'Вход...' : 'Регистрация...' }}
          </span>
          <span v-else>
            {{ activeTab === 'login' ? 'Войти' : 'Зарегистрироваться' }}
          </span>
        </button>

        <!-- Сообщение об ошибке -->
        <p v-if="apiError" class="mt-4 text-sm text-center text-red-500">
          {{ apiError }}
        </p>
      </form>
    </div>
  </div>
</template>

<script setup>
import { ref, reactive } from 'vue'
import { useRouter } from 'vue-router'
import { useAuthStore } from '../stores/authStore'
import { LoaderIcon } from 'lucide-vue-next'

const router = useRouter()
const authStore = useAuthStore()

const activeTab = ref('login')
const isLoading = ref(false)
const apiError = ref('')

const form = reactive({
  username: '',
  email: '',
  password: '',
})

const errors = reactive({
  username: '',
  email: '',
  password: '',
})

function validateForm() {
  let isValid = true
  errors.username = ''
  errors.email = ''
  errors.password = ''

  // Валидация username для регистрации
  if (activeTab.value === 'register') {
    if (!form.username) {
      errors.username = 'Введите имя пользователя'
      isValid = false
    } else if (form.username.length < 3 || form.username.length > 50) {
      errors.username = 'Имя должно быть от 3 до 50 символов'
      isValid = false
    }
  }

  // Валидация email
  const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/
  if (!form.email) {
    errors.email = 'Введите email'
    isValid = false
  } else if (!emailRegex.test(form.email)) {
    errors.email = 'Введите корректный email'
    isValid = false
  }

  // Валидация password
  if (!form.password) {
    errors.password = 'Введите пароль'
    isValid = false
  } else if (form.password.length < 8) {
    errors.password = 'Пароль должен быть не менее 8 символов'
    isValid = false
  }

  return isValid
}

async function handleSubmit() {
  if (!validateForm()) return

  isLoading.value = true
  apiError.value = ''

  try {
    if (activeTab.value === 'login') {
      // Логин
      const success = await authStore.login({
        username: form.email, // Изменено с email на username
        password: form.password,
      })

      if (success) {
        router.push('/')
      }
    } else {
      // Регистрация
      const success = await authStore.register({
        username: form.username,
        email: form.email,
        password: form.password,
      })

      if (success) {
        // После успешной регистрации делаем автологин
        const loginSuccess = await authStore.login({
          username: form.email, // Изменено с email на username
          password: form.password,
        })

        if (loginSuccess) {
          router.push('/')
        }
      }
    }
  } catch (error) {
    apiError.value = error.response?.data?.detail || 'Произошла ошибка'
  } finally {
    isLoading.value = false
  }
}
</script>

<style scoped>
/* ...existing styles... */
</style>
