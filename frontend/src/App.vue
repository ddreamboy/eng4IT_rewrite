<!-- frontend/src/App.vue -->
<template>
  <div class="min-h-screen bg-light-primary dark:bg-dark-primary">
    <!-- Desktop Navigation -->
    <nav
      class="hidden md:flex h-16 items-center justify-between px-6 shadow-md bg-light-secondary dark:bg-dark-secondary"
    >
      <div class="flex items-center space-x-8">
        <RouterLink to="/" class="text-2xl font-bold text-light-accent dark:text-dark-accent">
          Eng4IT
        </RouterLink>
        <div class="flex space-x-4">
          <RouterLink
            v-for="item in navigation"
            :key="item.path"
            :to="item.path"
            class="px-4 py-2 rounded hover:bg-white/10"
            :class="{ 'text-light-accent dark:text-dark-accent': route.path === item.path }"
          >
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
    <nav
      class="md:hidden flex h-16 items-center justify-between px-4 bg-light-secondary dark:bg-dark-secondary"
    >
      <RouterLink to="/" class="text-xl font-bold text-light-accent dark:text-dark-accent">
        Eng4IT
      </RouterLink>
      <div class="flex items-center space-x-4">
        <ThemeSwitcher />
        <UserMenu />
      </div>
    </nav>

    <!-- Main Content -->
    <main class="container mx-auto p-6 pb-20 md:pb-6">
      <RouterView />
    </main>

    <!-- Mobile Bottom Navigation -->
    <MobileNavigation />
  </div>
</template>

<script setup>
import { useRoute } from 'vue-router'
import { RouterLink, RouterView } from 'vue-router'
import ThemeSwitcher from './components/ThemeSwitcher.vue'
import UserMenu from './components/UserMenu.vue'
import MobileNavigation from './components/MobileNavigation.vue'

const route = useRoute()

const navigation = [
  { name: 'Главная', path: '/' },
  { name: 'Задания', path: '/tasks' },
  { name: 'Термины', path: '/terms' },
  { name: 'Профиль', path: '/profile' },
]
</script>
