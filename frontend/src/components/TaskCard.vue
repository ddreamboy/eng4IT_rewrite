// src/components/TaskCard.vue
<template>
    <div class="relative h-full">
        <div class="h-full rounded-lg shadow-md transition-all duration-300 hover:shadow-lg"
            :class="[themeStore.isDark ? 'bg-dark-secondary' : 'bg-light-secondary']">

            <!-- Кнопка информации -->
            <button @click.stop="toggleInfo" class="absolute top-3 right-3 p-2 rounded-full transition-colors z-10"
                :class="[
                    themeStore.isDark
                        ? 'bg-dark-primary hover:bg-dark-accent text-dark-text'
                        : 'bg-light-primary hover:bg-light-accent text-light-text'
                ]">
                <Info class="w-5 h-5 transition-transform duration-300" :class="{ 'rotate-180': expanded }" />
            </button>

            <!-- Основной контент -->
            <div class="p-6">
                <!-- Иконка и заголовок -->
                <div class="flex items-center space-x-4 mb-4">
                    <component :is="taskIcon" class="w-8 h-8"
                        :class="[themeStore.isDark ? 'text-dark-accent' : 'text-light-accent']" />
                    <h3 class="text-lg font-semibold"
                        :class="[themeStore.isDark ? 'text-dark-text' : 'text-light-text']">
                        {{ task.title }}
                    </h3>
                </div>

                <!-- Навыки -->
                <div class="flex flex-wrap gap-2">
                    <span v-for="skill in task.skills" :key="skill" class="px-2 py-1 text-xs rounded-full" :class="[
                        themeStore.isDark
                            ? 'bg-dark-primary text-dark-text'
                            : 'bg-light-primary text-light-text'
                    ]">
                        {{ skill }}
                    </span>
                </div>

                <!-- Расширенная информация -->
                <div class="overflow-hidden transition-all duration-300" :class="{ 'mt-6': expanded }"
                    :style="{ maxHeight: expanded ? '1000px' : '0px' }">

                    <div class="border-t pt-4"
                        :class="[themeStore.isDark ? 'border-dark-primary' : 'border-light-primary']">
                        <p class="mb-4 text-sm" :class="[themeStore.isDark ? 'text-dark-text' : 'text-light-text']">
                            {{ task.description }}
                        </p>

                        <!-- Уровни сложности -->
                        <div class="mb-4">
                            <h4 class="text-sm font-semibold mb-2"
                                :class="[themeStore.isDark ? 'text-dark-text' : 'text-light-text']">
                                Уровни сложности:
                            </h4>
                            <div class="flex gap-2">
                                <span v-for="level in task.difficulty_levels" :key="level"
                                    class="px-2 py-1 text-xs rounded-full" :class="[
                                        themeStore.isDark
                                            ? 'bg-dark-primary text-dark-accent'
                                            : 'bg-light-primary text-light-accent'
                                    ]">
                                    {{ level }}
                                </span>
                            </div>
                        </div>

                        <!-- Пример задания -->
                        <div v-if="task.example" class="text-sm">
                            <h4 class="font-semibold mb-2"
                                :class="[themeStore.isDark ? 'text-dark-text' : 'text-light-text']">
                                Пример:
                            </h4>
                            <pre class="p-3 rounded-lg whitespace-pre-wrap text-xs" :class="[
                                themeStore.isDark
                                    ? 'bg-dark-primary text-dark-text'
                                    : 'bg-light-primary text-light-text'
                            ]">{{ JSON.stringify(task.example, null, 2) }}</pre>
                        </div>
                    </div>
                </div>
            </div>
        </div>
    </div>
</template>

<script setup>
import { ref, computed } from 'vue'
import { useRouter } from 'vue-router'
import { useThemeStore } from '@/stores/themeStore'
import {
    MessageSquare,
    Link2,
    Book,
    Languages,
    Mail,
    Info
} from 'lucide-vue-next'

const props = defineProps({
    task: {
        type: Object,
        required: true
    }
})

const router = useRouter()
const themeStore = useThemeStore()
const expanded = ref(false)

// Маппинг иконок для разных типов заданий
const taskIcons = {
    'chat_dialog': MessageSquare,
    'word_matching': Link2,
    'term_definition': Book,
    'word_translation': Languages,
    'email_structure': Mail
}

// Получаем иконку для текущего типа задания
const taskIcon = computed(() => taskIcons[props.task.id] || MessageSquare)

// Простое переключение expanded состояния
function toggleInfo() {
    expanded.value = !expanded.value
}
</script>