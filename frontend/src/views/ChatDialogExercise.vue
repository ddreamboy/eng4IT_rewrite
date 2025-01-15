<!-- src/views/ChatDialogExercise.vue -->
<script setup>
import { ref, onMounted, computed, nextTick } from 'vue'
import { useThemeStore } from '@/stores/themeStore'
import { useAuthStore } from '@/stores/authStore'
import axios from 'axios'

const themeStore = useThemeStore()
const authStore = useAuthStore()

const loading = ref(false)
const userProfile = ref(null)
const exercise = ref(null)
const selectedAnswers = ref({})
const answerChecked = ref(false)
const isCorrect = ref(false)
const showTranslation = ref(false)
const currentMessageIndex = ref(0)
const isTyping = ref(false)
const chatContainer = ref(null) // Ссылка на контейнер чата

// Получение профиля пользователя
async function fetchUserProfile() {
    try {
        const response = await axios.get('/api/v1/users/profile')
        userProfile.value = response.data
    } catch (error) {
        console.error('Error fetching user profile:', error)
    }
}

// Генерация упражнения
async function generateExercise() {
    loading.value = true
    try {
        const request_params = {
            task_type: 'chat_dialog',
            user_id: authStore.user?.id,
            params: {
                difficulty: userProfile.value?.current_level || 'basic',
            },
        }

        const response = await axios.post('/api/v1/tasks/generate/chat-dialog', request_params)
        exercise.value = response.data

        // Сбрасываем состояние
        selectedAnswers.value = {}
        answerChecked.value = false
        isCorrect.value = false
        showTranslation.value = false
        currentMessageIndex.value = 0

        // Прокручиваем вниз после загрузки нового задания
        nextTick(() => {
            if (chatContainer.value) {
                chatContainer.value.scrollTop = chatContainer.value.scrollHeight
            }
        })
    } catch (err) {
        console.error('Error generating exercise:', err)
    } finally {
        loading.value = false
    }
}

// Проверка ответа
async function checkAnswer() {
    if (Object.keys(selectedAnswers.value).length === 0) return

    answerChecked.value = true
    loading.value = true

    try {
        // Проверяем, что exercise.value и его свойства существуют
        if (!exercise.value || !exercise.value.result || !exercise.value.result.content) {
            throw new Error('Invalid exercise data')
        }

        // Формируем правильные ответы
        const correctAnswers = exercise.value.result.content.messages
            .filter(msg => msg.is_user_message)
            .flatMap(msg => msg.gaps.map(gap => ({ [gap.id]: gap.correct })))
            .reduce((acc, val) => ({ ...acc, ...val }), {})

        // Формируем used_items и item_types
        const usedItems = exercise.value.metadata?.used_terms || []
        const itemTypes = exercise.value.metadata?.used_terms?.reduce((acc, term) => ({ ...acc, [term]: 'term' }), {}) || {}

        const response = await axios.post('/api/v1/tasks/generate/chat-dialog/validate', {
            task_id: exercise.value.task_id,
            user_answers: selectedAnswers.value,
            correct_answers: correctAnswers,
            used_items: usedItems,
            item_types: itemTypes,
            user_id: authStore.user?.id,
        })

        isCorrect.value = response.data.is_successful

        if (isCorrect.value) {
            // Автоматически генерируем новое задание через задержку
            setTimeout(() => {
                generateExercise()
            }, 1500)
        }
    } catch (error) {
        console.error('Error validating answer:', error)
        alert('Произошла ошибка при проверке ответа. Попробуйте еще раз.')
    } finally {
        loading.value = false
    }
}

// Обработка выбора ответа
function selectAnswer(gapId, answer) {
    selectedAnswers.value[gapId] = answer
}

// Переключение видимости перевода
function toggleTranslation() {
    showTranslation.value = !showTranslation.value
}

// Инициализация при монтировании
onMounted(async () => {
    await fetchUserProfile()
    generateExercise()
})
</script>

<template>
    <div class="container mx-auto px-4 py-8">
        <!-- Заголовок -->
        <header class="text-center mb-8">
            <h1 class="text-2xl font-bold mb-2" :class="[themeStore.isDark ? 'text-dark-text' : 'text-light-text']">
                Чат-диалог
            </h1>
            <p class="text-sm" :class="[themeStore.isDark ? 'text-dark-text/70' : 'text-light-text/70']">
                Заполните пропуски в диалоге, выбрав правильные слова
            </p>
        </header>

        <div class="max-w-2xl mx-auto">
            <!-- Карточка с упражнением -->
            <div v-if="exercise" class="p-6 rounded-lg shadow-lg transition-all duration-300" :class="[
                themeStore.isDark
                    ? 'bg-dark-secondary hover:shadow-dark-accent/20'
                    : 'bg-light-secondary hover:shadow-light-accent/20',
            ]">
                <!-- Контейнер для чата с прокруткой -->
                <div ref="chatContainer" class="overflow-y-auto max-h-[500px] mb-6 pr-4">
                    <!-- Сообщения чата -->
                    <div v-for="(message, index) in exercise.result.content.messages" :key="index" class="mb-6">
                        <!-- Сообщение собеседника -->
                        <div v-if="!message.is_user_message" class="flex items-start space-x-4">
                            <div class="flex-1">
                                <div class="text-sm font-medium"
                                    :class="[themeStore.isDark ? 'text-dark-text' : 'text-light-text']">
                                    {{ message.author }}
                                </div>
                                <div class="mt-1 p-4 rounded-lg"
                                    :class="[themeStore.isDark ? 'bg-dark-primary/50' : 'bg-light-primary/50']">
                                    <p class="text-lg"
                                        :class="[themeStore.isDark ? 'text-dark-text' : 'text-light-text']">
                                        {{ message.text }}
                                    </p>
                                    <!-- Кнопка показа перевода -->
                                    <button @click="toggleTranslation"
                                        class="mt-2 px-4 py-2 text-sm rounded-lg transition-all duration-300 transform hover:scale-105"
                                        :class="[
                                            themeStore.isDark
                                                ? 'bg-dark-accent/20 text-dark-text hover:bg-dark-accent/30'
                                                : 'bg-light-accent/20 text-light-text hover:bg-light-accent/30',
                                        ]">
                                        {{ showTranslation ? 'Скрыть перевод' : 'Показать перевод' }}
                                    </button>
                                    <!-- Перевод сообщения -->
                                    <p v-if="showTranslation" class="text-lg mt-2 transition-all duration-300"
                                        :class="[themeStore.isDark ? 'text-dark-text/80' : 'text-light-text/80']">
                                        {{ message.translation }}
                                    </p>
                                </div>
                            </div>
                        </div>

                        <!-- Сообщение пользователя -->
                        <div v-if="message.is_user_message" class="flex items-start space-x-4 justify-end">
                            <div class="flex-1">
                                <div class="text-sm font-medium text-right"
                                    :class="[themeStore.isDark ? 'text-dark-text' : 'text-light-text']">
                                    Вы
                                </div>
                                <div class="mt-1 p-4 rounded-lg"
                                    :class="[themeStore.isDark ? 'bg-dark-primary/50' : 'bg-light-primary/50']">
                                    <p class="text-lg"
                                        :class="[themeStore.isDark ? 'text-dark-text' : 'text-light-text']">
                                        {{ message.text }}
                                    </p>
                                    <!-- Варианты ответов -->
                                    <div v-for="gap in message.gaps" :key="gap.id" class="mt-4">
                                        <div class="grid grid-cols-2 gap-4">
                                            <button v-for="option in gap.options" :key="option.word"
                                                @click="selectAnswer(gap.id, option.word)" :disabled="answerChecked"
                                                class="p-2 rounded-lg text-left transition-all duration-300 transform hover:scale-105 shadow-sm"
                                                :class="[
                                                    themeStore.isDark
                                                        ? 'bg-dark-primary text-dark-text hover:bg-dark-primary/80'
                                                        : 'bg-light-primary text-light-text hover:bg-light-primary/80',
                                                    selectedAnswers[gap.id] === option.word ? 'ring-2 ring-blue-500' : '',
                                                ]">
                                                {{ option.word }}
                                            </button>
                                        </div>
                                    </div>
                                </div>
                            </div>
                        </div>
                    </div>
                </div>

                <!-- Кнопка проверки ответа -->
                <button @click="checkAnswer"
                    class="mt-4 px-6 py-2 rounded-lg font-medium transition-all duration-300 shadow-md transform hover:scale-105"
                    :class="[
                        themeStore.isDark
                            ? 'bg-dark-accent text-dark-text hover:bg-dark-accent/90'
                            : 'bg-light-accent text-light-text hover:bg-light-accent/90',
                    ]">
                    Проверить ответ
                </button>
            </div>
        </div>
    </div>
</template>

<style scoped>
.container {
    min-height: calc(100vh - 4rem);
}

.transition-all {
    transition-property: all;
    transition-timing-function: cubic-bezier(0.4, 0, 0.2, 1);
    transition-duration: 300ms;
}

/* Стили для прокрутки */
.max-h-[500px] {
    max-height: 500px;
}

.overflow-y-auto {
    overflow-y: auto;
}

.pr-4 {
    padding-right: 1rem;
}

/* Стили для скроллбара */
::-webkit-scrollbar {
    width: 8px;
}

::-webkit-scrollbar-track {
    background: transparent;
}

::-webkit-scrollbar-thumb {
    background: #888;
    border-radius: 4px;
}

::-webkit-scrollbar-thumb:hover {
    background: #555;
}
</style>