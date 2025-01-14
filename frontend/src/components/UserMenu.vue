// src/components/UserMenu.vue
<template>
    <div class="relative">
        <button @click="isOpen = !isOpen"
            class="flex items-center space-x-1 p-2 rounded-lg hover:bg-light-primary/10 dark:hover:bg-dark-primary/10">
            <div v-if="authStore.isAuthenticated"
                class="w-8 h-8 rounded-full bg-light-accent dark:bg-dark-accent flex items-center justify-center text-white">
                {{ authStore.userInitials }}
            </div>
            <svg v-else xmlns="http://www.w3.org/2000/svg" class="h-6 w-6" fill="none" viewBox="0 0 24 24"
                stroke="currentColor">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2"
                    d="M16 7a4 4 0 11-8 0 4 4 0 018 0zM12 14a7 7 0 00-7 7h14a7 7 0 00-7-7z" />
            </svg>
        </button>

        <!-- Выпадающее меню -->
        <div v-if="isOpen"
            class="absolute right-0 mt-2 w-48 rounded-lg bg-light-secondary dark:bg-dark-secondary shadow-lg py-1">
            <template v-if="authStore.isAuthenticated">
                <router-link to="/profile"
                    class="block px-4 py-2 hover:bg-light-primary/10 dark:hover:bg-dark-primary/10"
                    @click="isOpen = false">
                    Профиль
                </router-link>
                <button @click="handleLogout"
                    class="block w-full text-left px-4 py-2 hover:bg-light-primary/10 dark:hover:bg-dark-primary/10 text-red-500">
                    Выйти
                </button>
            </template>
            <template v-else>
                <router-link to="/auth" class="block px-4 py-2 hover:bg-light-primary/10 dark:hover:bg-dark-primary/10"
                    @click="isOpen = false">
                    Войти
                </router-link>
            </template>
        </div>
    </div>
</template>

<script setup>
import { ref } from 'vue'
import { useRouter } from 'vue-router'
import { useAuthStore } from '@/stores/authStore'

const router = useRouter()
const authStore = useAuthStore()
const isOpen = ref(false)

async function handleLogout() {
    authStore.logout()
    isOpen.value = false
    router.push('/auth')
}
</script>