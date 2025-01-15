// src/components/TaskCard.vue
<template>
    <div class="relative h-full">
        <!-- Основная карточка -->
        <div class="relative h-full rounded-lg shadow-md transition-all duration-500 ease-in-out overflow-hidden"
            :class="[
                themeStore.isDark ? 'bg-dark-secondary' : 'bg-light-secondary',
                expanded ? 'fixed inset-x-4 md:absolute md:inset-x-0 z-30' : 'hover:shadow-lg'
            ]" :style="{
                top: expanded ? `${cardTop}px` : '0',
                width: expanded ? `${cardWidth}px` : 'auto',
                maxHeight: expanded ? `${maxHeight}px` : 'none',
            }">


            <div v-if="expanded" class="fixed inset-0 bg-black/20 z-20" @click.stop="toggleInfo">
            </div>

            <!-- Placeholder для сохранения размера в сетке -->
            <div v-if="expanded" class="h-full rounded-lg invisible">
                <!-- Копия содержимого для поддержания размера -->
                <div class="p-6">
                    <div class="flex items-center space-x-4 mb-4">
                        <div class="w-8 h-8"></div>
                        <div class="h-6"></div>
                    </div>
                    <div class="flex flex-wrap gap-2">
                        <span v-for="skill in task.skills" :key="skill" class="px-2 py-1 invisible">
                            {{ skill }}
                        </span>
                    </div>
                </div>
            </div>
            <!-- Кнопка информации -->
            <button @click.stop="toggleInfo" class="absolute top-3 right-3 p-2 rounded-full transition-colors" :class="[
                themeStore.isDark
                    ? 'bg-dark-primary hover:bg-dark-accent text-dark-text'
                    : 'bg-light-primary hover:bg-light-accent text-light-text'
            ]">
                <Info class="w-5 h-5 transition-transform duration-500" :class="{ 'rotate-180': expanded }" />
            </button>

            <!-- Основной контент -->
            <div class="p-6 cursor-pointer" @click="navigateToTask">
                <!-- Иконка и заголовок -->
                <div class="flex items-center space-x-4 mb-4">
                    <component :is="taskIcon" class="w-8 h-8" :class="[
                        themeStore.isDark ? 'text-dark-accent' : 'text-light-accent'
                    ]" />
                    <h3 class="text-lg font-semibold" :class="[
                        themeStore.isDark ? 'text-dark-text' : 'text-light-text'
                    ]">{{ task.title }}</h3>
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
                <div class="transition-all duration-500 ease-in-out overflow-hidden"
                    :class="expanded ? 'mt-6 pt-6 opacity-100' : 'max-h-0 opacity-0'">
                    <div class="border-t" :class="[
                        themeStore.isDark ? 'border-dark-primary' : 'border-light-primary'
                    ]">
                        <p class="mb-4 mt-4 text-sm" :class="[
                            themeStore.isDark ? 'text-dark-text' : 'text-light-text'
                        ]">
                            {{ task.description }}
                        </p>

                        <!-- Уровни сложности -->
                        <div class="mb-4">
                            <h4 class="text-sm font-semibold mb-2" :class="[
                                themeStore.isDark ? 'text-dark-text' : 'text-light-text'
                            ]">
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
                            <h4 class="font-semibold mb-2" :class="[
                                themeStore.isDark ? 'text-dark-text' : 'text-light-text'
                            ]">
                                Пример:
                            </h4>
                            <pre class="p-3 rounded-lg whitespace-pre-wrap text-xs" :class="[
                                themeStore.isDark ? 'bg-dark-primary text-dark-text' : 'bg-light-primary text-light-text'
                            ]">{{ JSON.stringify(task.example, null, 2) }}</pre>
                        </div>
                    </div>
                </div>
            </div>
        </div>

        <!-- Затемнение на весь экран -->
        <div v-if="expanded" class="fixed inset-0 bg-black/20 z-20" @click.stop="toggleInfo"></div>

        <!-- Placeholder для сохранения размера в сетке -->
        <div v-if="expanded" class="h-full rounded-lg invisible">
            <!-- Копия содержимого для поддержания размера -->
            <div class="p-6">
                <div class="flex items-center space-x-4 mb-4">
                    <div class="w-8 h-8"></div>
                    <div class="h-6"></div>
                </div>
                <div class="flex flex-wrap gap-2">
                    <span v-for="skill in task.skills" :key="skill" class="px-2 py-1 invisible">
                        {{ skill }}
                    </span>
                </div>
            </div>
        </div>
    </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
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
const cardEl = ref(null)
const cardTop = ref(0)
const cardWidth = ref(0)
const maxHeight = ref(0)

// Получаем иконку для текущего типа задания
const taskIcon = computed(() => taskIcons[props.task.id] || MessageSquare)

// Переключение расширенной информации
// Модифицируем функцию toggleInfo
function toggleInfo() {
    if (!expanded.value) {
        // Сохраняем текущую позицию и размеры перед раскрытием
        const rect = cardEl.value.getBoundingClientRect()
        cardTop.value = rect.top
        cardWidth.value = rect.width
        maxHeight.value = window.innerHeight - 40 // отступ сверху и снизу
        expanded.value = true
        document.body.style.overflow = 'hidden' // Блокируем прокрутку
    } else {
        expanded.value = false
        document.body.style.overflow = '' // Возвращаем прокрутку
    }
}

// Добавляем слушатель изменения размера окна
onMounted(() => {
    window.addEventListener('resize', () => {
        if (expanded.value) {
            const rect = cardEl.value.getBoundingClientRect()
            cardWidth.value = rect.width
            maxHeight.value = window.innerHeight - 40
        }
    })
})

// Навигация к заданию (заглушка)
function navigateToTask() {
    console.log(`Переход к заданию ${props.task.id}`)
    // router.push(`/tasks/${props.task.id}`)
}
</script>