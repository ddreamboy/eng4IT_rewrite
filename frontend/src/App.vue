// src/App.vue
<template>
  <div
    class="min-h-screen transition-colors duration-200"
    :class="[
      themeStore.isDark
        ? 'dark bg-dark-primary text-dark-text'
        : 'bg-light-primary text-light-text',
    ]"
  >
    <!-- Скроем навигацию если мы на странице авторизации -->
    <template v-if="!isAuthPage">
      <!-- Desktop Navigation -->
      <nav
        class="hidden md:flex h-16 items-center justify-between px-6 shadow-md"
        :class="[themeStore.isDark ? 'bg-dark-secondary' : 'bg-light-secondary']"
      >
        <div class="flex items-center space-x-8">
          <RouterLink
            to="/"
            class="text-2xl font-bold transition-colors"
            :class="[themeStore.isDark ? 'text-dark-accent' : 'text-light-accent']"
          >
            Eng4IT
          </RouterLink>
          <div class="flex space-x-4">
            <RouterLink
              v-for="item in navigation"
              :key="item.path"
              :to="item.path"
              class="px-4 py-2 rounded transition-colors"
              :class="[
                route.path === item.path
                  ? [themeStore.isDark ? 'text-dark-accent' : 'text-light-accent']
                  : [
                      themeStore.isDark
                        ? 'text-dark-text hover:bg-dark-primary/50'
                        : 'text-light-text hover:bg-light-primary/50',
                    ],
              ]"
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
        class="md:hidden flex h-16 items-center justify-between px-4"
        :class="[themeStore.isDark ? 'bg-dark-secondary' : 'bg-light-secondary']"
      >
        <RouterLink
          to="/"
          class="text-xl font-bold transition-colors"
          :class="[themeStore.isDark ? 'text-dark-accent' : 'text-light-accent']"
        >
          Eng4IT
        </RouterLink>
        <div class="flex items-center space-x-4">
          <ThemeSwitcher />
          <UserMenu />
        </div>
      </nav>
    </template>

    <main :class="[isAuthPage ? 'min-h-screen' : 'container mx-auto p-6 pb-20 md:pb-6']">
      <RouterView />
    </main>

    <MobileNavigation v-if="!isAuthPage" />
  </div>
</template>

<script setup>
import { computed } from 'vue'
import { useRoute } from 'vue-router'
import { RouterLink, RouterView } from 'vue-router'
import { useThemeStore } from '@/stores/themeStore'
import ThemeSwitcher from './components/ThemeSwitcher.vue'
import UserMenu from './components/UserMenu.vue'
import MobileNavigation from './components/MobileNavigation.vue'
import { HomeIcon, BookOpenIcon, AcademicCapIcon, UserIcon } from '@heroicons/vue/24/outline'

const route = useRoute()
const themeStore = useThemeStore()
const isAuthPage = computed(() => route.name === 'auth')

const navigation = [
  { name: 'Главная', path: '/', icon: HomeIcon },
  { name: 'Словарь', path: '/dictionary', icon: BookOpenIcon },
  { name: 'Профиль', path: '/profile', icon: UserIcon },
]
</script>
