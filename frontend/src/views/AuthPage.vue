// src/views/AuthPage.vue
<template>
    <div class="min-h-screen w-full flex items-center justify-center"
        :class="[themeStore.isDark ? 'bg-dark-primary' : 'bg-light-primary']">
        <div class="w-full max-w-md p-6 m-4 rounded-lg shadow-lg"
            :class="[themeStore.isDark ? 'bg-dark-secondary' : 'bg-light-secondary']">
            <!-- Переключатель форм -->
            <div class="flex p-1 mb-6 rounded-lg" :class="[themeStore.isDark ? 'bg-dark-primary' : 'bg-light-primary']">
                <button v-for="tab in ['login', 'register']" :key="tab" @click="activeTab = tab"
                    class="flex-1 py-2 text-center rounded-md transition-colors" :class="[
                        activeTab === tab
                            ? [themeStore.isDark ? 'bg-dark-accent text-dark-text' : 'bg-light-accent text-light-text']
                            : [themeStore.isDark ? 'text-dark-text hover:bg-dark-primary/50' : 'text-light-text hover:bg-light-primary/50']
                    ]">
                    {{ tab === 'login' ? 'Вход' : 'Регистрация' }}
                </button>
            </div>

            <!-- Форма -->
            <form @submit.prevent="handleSubmit" class="space-y-4">
                <!-- Username для регистрации -->
                <div v-if="activeTab === 'register'" class="space-y-1">
                    <label class="block text-sm" :class="[themeStore.isDark ? 'text-dark-text' : 'text-light-text']">
                        Имя пользователя
                    </label>
                    <input v-model="form.username" type="text" class="w-full p-2 rounded border transition-colors"
                        :class="[
                            themeStore.isDark
                                ? 'bg-dark-primary border-dark-secondary text-dark-text focus:border-dark-accent'
                                : 'bg-light-primary border-light-secondary text-light-text focus:border-light-accent',
                            errors.username ? 'border-red-500' : ''
                        ]" placeholder="john_doe" />
                    <p v-if="errors.username" class="text-sm text-red-500">{{ errors.username }}</p>
                </div>

                <!-- Email -->
                <div class="space-y-1">
                    <label class="block text-sm" :class="[themeStore.isDark ? 'text-dark-text' : 'text-light-text']">
                        Email
                    </label>
                    <input v-model="form.email" type="email" class="w-full p-2 rounded border transition-colors" :class="[
                        themeStore.isDark
                            ? 'bg-dark-primary border-dark-secondary text-dark-text focus:border-dark-accent'
                            : 'bg-light-primary border-light-secondary text-light-text focus:border-light-accent',
                        errors.email ? 'border-red-500' : ''
                    ]" placeholder="user@example.com" />
                    <p v-if="errors.email" class="text-sm text-red-500">{{ errors.email }}</p>
                </div>

                <!-- Password -->
                <div class="space-y-1">
                    <label class="block text-sm" :class="[themeStore.isDark ? 'text-dark-text' : 'text-light-text']">
                        Пароль
                    </label>
                    <input v-model="form.password" type="password" class="w-full p-2 rounded border transition-colors"
                        :class="[
                            themeStore.isDark
                                ? 'bg-dark-primary border-dark-secondary text-dark-text focus:border-dark-accent'
                                : 'bg-light-primary border-light-secondary text-light-text focus:border-light-accent',
                            errors.password ? 'border-red-500' : ''
                        ]" placeholder="••••••••" />
                    <p v-if="errors.password" class="text-sm text-red-500">{{ errors.password }}</p>
                </div>

                <button type="submit" class="w-full py-2 text-white rounded-lg transition-colors disabled:opacity-50"
                    :class="[themeStore.isDark ? 'bg-dark-accent hover:bg-dark-accent/90' : 'bg-light-accent hover:bg-light-accent/90']"
                    :disabled="isLoading">
                    <template v-if="isLoading">
                        <span class="flex items-center justify-center">
                            <svg class="animate-spin -ml-1 mr-2 h-4 w-4 text-white" fill="none" viewBox="0 0 24 24">
                                <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor"
                                    stroke-width="4" />
                                <path class="opacity-75" fill="currentColor"
                                    d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4z" />
                            </svg>
                            {{ activeTab === 'login' ? 'Вход...' : 'Регистрация...' }}
                        </span>
                    </template>
                    <template v-else>
                        {{ activeTab === 'login' ? 'Войти' : 'Зарегистрироваться' }}
                    </template>
                </button>

                <p v-if="error" class="text-sm text-center text-red-500 mt-4">
                    {{ error }}
                </p>
            </form>
        </div>
    </div>
</template>

<script setup>
import { ref, reactive } from 'vue'
import { useRouter } from 'vue-router'
import { useAuthStore } from '@/stores/authStore'
import { useThemeStore } from '@/stores/themeStore'

const router = useRouter()
const authStore = useAuthStore()
const themeStore = useThemeStore()

// State
const activeTab = ref('login')
const isLoading = ref(false)
const error = ref('')

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

// Form validation
function validateForm() {
    let isValid = true
    errors.username = ''
    errors.email = ''
    errors.password = ''

    // Validate username for registration
    if (activeTab.value === 'register') {
        if (!form.username) {
            errors.username = 'Введите имя пользователя'
            isValid = false
        } else if (form.username.length < 3 || form.username.length > 50) {
            errors.username = 'Имя должно быть от 3 до 50 символов'
            isValid = false
        }
    }

    // Validate email
    const emailRegex = /^[^\s@]+@[^\s@]+\.[a-zA-Z]{2,}$/
    if (!form.email) {
        errors.email = 'Введите email'
        isValid = false
    } else if (!emailRegex.test(form.email)) {
        errors.email = 'Введите корректный email (например, user@example.com)'
        isValid = false
    } else {
        // Проверяем домен
        const domain = form.email.split('@')[1]
        const invalidDomains = ['test', 'localhost']
        if (invalidDomains.some(d => domain.includes(d))) {
            errors.email = 'Используйте действительный домен email (например, gmail.com, mail.ru)'
            isValid = false
        }
    }

    // Validate password
    if (!form.password) {
        errors.password = 'Введите пароль'
        isValid = false
    } else if (form.password.length < 8) {
        errors.password = 'Пароль должен быть не менее 8 символов'
        isValid = false
    }

    return isValid
}

// Form submission
async function handleSubmit() {
    if (!validateForm()) return

    isLoading.value = true
    error.value = ''

    try {
        if (activeTab.value === 'login') {
            const success = await authStore.login({
                username: form.email,
                password: form.password,
            })

            if (success) {
                router.push('/')
            }
        } else {
            const success = await authStore.register({
                username: form.username,
                email: form.email,
                password: form.password,
            })

            if (success) {
                // Auto-login after successful registration
                const loginSuccess = await authStore.login({
                    username: form.email,
                    password: form.password,
                })

                if (loginSuccess) {
                    router.push('/')
                }
            }
        }
    } catch (err) {
        error.value = err.response?.data?.detail || 'Произошла ошибка'
    } finally {
        isLoading.value = false
    }
}
</script>