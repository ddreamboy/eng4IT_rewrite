<!-- frontend/src/components/MobileNavigation.vue -->
<template>
  <nav
    class="md:hidden fixed bottom-0 inset-x-0 h-16 flex items-center justify-around bg-light-secondary dark:bg-dark-secondary shadow-lg"
  >
    <RouterLink
      v-for="item in navigation"
      :key="item.path"
      :to="item.path"
      class="flex flex-col items-center p-2"
      :class="[
        route.path === item.path ? 'text-light-accent dark:text-dark-accent' : 'text-gray-500',
      ]"
    >
      <component :is="item.icon" class="w-6 h-6" />
      <span class="text-xs mt-1">{{ item.name }}</span>
    </RouterLink>
  </nav>
</template>

<script setup>
import { useRoute } from 'vue-router'
import { Home, BookOpen, GraduationCap, User } from 'lucide-vue-next'

const route = useRoute()

const navigation = [
  { name: 'Главная', path: '/', icon: Home },
  { name: 'Задания', path: '/tasks', icon: BookOpen },
  { name: 'Термины', path: '/terms', icon: GraduationCap },
  { name: 'Профиль', path: '/profile', icon: User },
]
</script>
