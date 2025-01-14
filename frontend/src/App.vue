// src/App.vue
<template>
  <div class="min-h-screen bg-dark-primary dark:bg-dark-primary">
    <!-- Скроем навигацию если мы на странице авторизации -->
    <template v-if="!isAuthPage">
      <!-- Desktop Navigation -->
      <nav
        class="hidden md:flex h-16 items-center justify-between px-6 shadow-md bg-dark-secondary dark:bg-dark-secondary">
        <div class="flex items-center space-x-8">
          <RouterLink to="/" class="text-2xl font-bold text-dark-accent dark:text-dark-accent">
            Eng4IT
          </RouterLink>
          <div class="flex space-x-4">
            <RouterLink v-for="item in navigation" :key="item.path" :to="item.path"
              class="px-4 py-2 rounded hover:bg-white/10"
              :class="{ 'text-dark-accent dark:text-dark-accent': route.path === item.path }">
              {{ item.name }}
            </RouterLink>
          </div>
        </div>
        <div class="flex items-center space-x-4">
          <ThemeSwitcher />
          <UserMenu />
        </div>
      </nav>

      <!-- Mobile Header -->
      <nav class="md:hidden flex h-16 items-center justify-between px-4 bg-dark-secondary dark:bg-dark-secondary">
        <RouterLink to="/" class="text-xl font-bold text-dark-accent dark:text-dark-accent">
          Eng4IT
        </RouterLink>
        <div class="flex items-center space-x-4">
          <ThemeSwitcher />
          <UserMenu />
        </div>
      </nav>
    </template>

    <!-- Main Content -->
    <main :class="[
      isAuthPage ? 'min-h-screen' : 'container mx-auto p-6 pb-20 md:pb-6'
    ]">
      <RouterView />
    </main>

    <!-- Mobile Bottom Navigation -->
    <MobileNavigation v-if="!isAuthPage" />
  </div>
</template>

<script setup>
import { computed } from 'vue'
import { useRoute } from 'vue-router'
import { RouterLink, RouterView } from 'vue-router'
import ThemeSwitcher from './components/ThemeSwitcher.vue'
import UserMenu from './components/UserMenu.vue'
import MobileNavigation from './components/MobileNavigation.vue'

const route = useRoute()
const isAuthPage = computed(() => route.name === 'auth')

const navigation = [
  { name: 'Главная', path: '/' },
]
</script>