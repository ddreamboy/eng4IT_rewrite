// src/views/AchievementsPage.vue

<template>
    <div class="container mx-auto px-4 py-2">
        <h1 class="text-2xl font-bold mb-8" :class="[themeStore.isDark ? 'text-dark-text' : 'text-light-text']">
            Достижения
        </h1>

        <!-- Дневные достижения -->
        <div class="mb-8 p-6 rounded-lg shadow-lg"
            :class="[themeStore.isDark ? 'bg-dark-secondary' : 'bg-light-secondary']">
            <h2 class="text-xl font-semibold mb-4" :class="[themeStore.isDark ? 'text-dark-text' : 'text-light-text']">
                Дневные цели
            </h2>
            <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
                <!-- Слова за день -->
                <div class="p-4 rounded-lg" :class="[themeStore.isDark ? 'bg-dark-primary' : 'bg-light-primary']">
                    <div class="flex justify-between items-center mb-2">
                        <span class="font-medium" :class="[themeStore.isDark ? 'text-dark-text' : 'text-light-text']">
                            Слова за день
                        </span>
                        <span :class="[
                            stats?.daily_stats?.goals_achieved?.words
                                ? 'text-green-500'
                                : themeStore.isDark ? 'text-dark-text/50' : 'text-light-text/50'
                        ]">
                            {{ stats?.daily_stats?.words || 0 }}/{{ stats?.daily_stats?.goals?.words || 0 }}
                        </span>
                    </div>
                    <div class="w-full bg-gray-200 rounded-full h-2.5">
                        <div class="h-full rounded-full transition-all duration-300"
                            :class="[themeStore.isDark ? 'bg-dark-accent' : 'bg-light-accent']"
                            :style="{ width: `${Math.min(((stats?.daily_stats?.words || 0) / (stats?.daily_stats?.goals?.words || 1)) * 100, 100)}%` }" />
                    </div>
                </div>

                <!-- Термины за день -->
                <div class="p-4 rounded-lg" :class="[themeStore.isDark ? 'bg-dark-primary' : 'bg-light-primary']">
                    <div class="flex justify-between items-center mb-2">
                        <span class="font-medium" :class="[themeStore.isDark ? 'text-dark-text' : 'text-light-text']">
                            Термины за день
                        </span>
                        <span :class="[
                            stats?.daily_stats?.goals_achieved?.terms
                                ? 'text-green-500'
                                : themeStore.isDark ? 'text-dark-text/50' : 'text-light-text/50'
                        ]">
                            {{ stats?.daily_stats?.terms || 0 }}/{{ stats?.daily_stats?.goals?.terms || 0 }}
                        </span>
                    </div>
                    <div class="w-full bg-gray-200 rounded-full h-2.5">
                        <div class="h-full rounded-full transition-all duration-300"
                            :class="[themeStore.isDark ? 'bg-dark-accent' : 'bg-light-accent']"
                            :style="{ width: `${Math.min(((stats?.daily_stats?.terms || 0) / (stats?.daily_stats?.goals?.terms || 1)) * 100, 100)}%` }" />
                    </div>
                </div>
            </div>
        </div>

        <!-- Общие достижения -->
        <div class="p-6 rounded-lg shadow-lg" :class="[themeStore.isDark ? 'bg-dark-secondary' : 'bg-light-secondary']">
            <h2 class="text-xl font-semibold mb-4" :class="[themeStore.isDark ? 'text-dark-text' : 'text-light-text']">
                Общий прогресс
            </h2>
            <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
                <!-- Всего слов -->
                <div class="p-4 rounded-lg" :class="[themeStore.isDark ? 'bg-dark-primary' : 'bg-light-primary']">
                    <div class="flex justify-between items-center mb-2">
                        <span class="font-medium" :class="[themeStore.isDark ? 'text-dark-text' : 'text-light-text']">
                            Найдено слов
                        </span>
                        <div class="text-right">
                            <span :class="[
                                stats?.total_stats?.goals_achieved?.words
                                    ? 'text-green-500'
                                    : themeStore.isDark ? 'text-dark-text/50' : 'text-light-text/50'
                            ]">
                                {{ stats?.total_stats?.total_words || 0 }}
                            </span>
                            <div class="text-xs opacity-50">
                                из {{ stats?.total_stats?.available?.total_available_words || 0 }} доступных
                            </div>
                        </div>
                    </div>
                    <div class="w-full bg-gray-200 rounded-full h-2.5">
                        <div class="h-full rounded-full transition-all duration-300"
                            :class="[themeStore.isDark ? 'bg-dark-accent' : 'bg-light-accent']"
                            :style="{ width: `${Math.min(((stats?.total_stats?.total_words || 0) / (stats?.total_stats?.goals?.words || 1)) * 100, 100)}%` }" />
                    </div>
                </div>

                <!-- Всего терминов -->
                <div class="p-4 rounded-lg" :class="[themeStore.isDark ? 'bg-dark-primary' : 'bg-light-primary']">
                    <div class="flex justify-between items-center mb-2">
                        <span class="font-medium" :class="[themeStore.isDark ? 'text-dark-text' : 'text-light-text']">
                            Найдено терминов
                        </span>
                        <div class="text-right">
                            <span :class="[
                                stats?.total_stats?.goals_achieved?.terms
                                    ? 'text-green-500'
                                    : themeStore.isDark ? 'text-dark-text/50' : 'text-light-text/50'
                            ]">
                                {{ stats?.total_stats?.total_terms || 0 }}
                            </span>
                            <div class="text-xs opacity-50">
                                из {{ stats?.total_stats?.available?.total_available_terms || 0 }} доступных
                            </div>
                        </div>
                    </div>
                    <div class="w-full bg-gray-200 rounded-full h-2.5">
                        <div class="h-full rounded-full transition-all duration-300"
                            :class="[themeStore.isDark ? 'bg-dark-accent' : 'bg-light-accent']"
                            :style="{ width: `${Math.min(((stats?.total_stats?.total_terms || 0) / (stats?.total_stats?.goals?.terms || 1)) * 100, 100)}%` }" />
                    </div>
                </div>
            </div>
        </div>
    </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useThemeStore } from '@/stores/themeStore'
import axios from 'axios'

const themeStore = useThemeStore()
const stats = ref(null)

async function fetchStats() {
    try {
        const response = await axios.get('/api/v1/achievements/stats')
        stats.value = response.data
    } catch (error) {
        console.error('Error fetching achievements:', error)
    }
}

onMounted(() => {
    fetchStats()
})
</script>