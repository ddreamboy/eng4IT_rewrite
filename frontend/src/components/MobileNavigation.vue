// src/components/MobileNavigation.vue
<template>
    <nav class="md:hidden fixed bottom-0 inset-x-0 h-16 bg-light-secondary dark:bg-dark-secondary shadow-lg">
        <div class="grid h-full grid-cols-4">
            <router-link v-for="item in navigation" :key="item.path" :to="item.path"
                class="flex flex-col items-center justify-center"
                :class="{ 'text-light-accent dark:text-dark-accent': route.path === item.path }">
                <component :is="item.icon" class="h-6 w-6" />
                <span class="text-xs mt-1">{{ item.name }}</span>
            </router-link>
        </div>
    </nav>
</template>

<script setup>
import { useRoute } from 'vue-router'
import {
    HomeIcon,
    BookOpenIcon,
    AcademicCapIcon,
    UserIcon
} from '@heroicons/vue/24/outline'

const route = useRoute()

const navigation = [
    { name: 'Главная', path: '/', icon: HomeIcon },
    { name: 'Профиль', path: '/profile', icon: UserIcon },
    { name: 'Словарь', path: '/dictionary', icon: BookOpenIcon },
]
</script>