// src/views/TermDefinitionExercise.vue
<template>
    <div class="container mx-auto px-4 py-8">
        <!-- Заголовок -->
        <header class="text-center mb-8">
            <h1 class="text-2xl font-bold mb-2" :class="[
                themeStore.isDark ? 'text-dark-text' : 'text-light-text'
            ]">
                Определение термина
            </h1>
            <p class="text-sm" :class="[
                themeStore.isDark ? 'text-dark-text/70' : 'text-light-text/70'
            ]">
                Сопоставьте термин с правильным определением
            </p>
        </header>

        <div class="max-w-2xl mx-auto">
            <!-- Настройки -->
            <div class="mb-8 p-6 rounded-lg shadow-lg transition-all duration-300" :class="[
                themeStore.isDark ? 'bg-dark-secondary hover:shadow-dark-accent/20' : 'bg-light-secondary hover:shadow-light-accent/20'
            ]">
                <div class="flex items-center justify-between">
                    <!-- Выбор категории -->
                    <div class="flex-1 max-w-xs">
                        <label class="block text-sm font-medium mb-2" :class="[
                            themeStore.isDark ? 'text-dark-text' : 'text-light-text'
                        ]">
                            Категория (необязательно)
                        </label>
                        <select v-model="settings.category"
                            class="w-full px-4 py-2 rounded-lg transition-all duration-300 shadow-sm" :class="[
                                themeStore.isDark
                                    ? 'bg-dark-primary text-dark-text border-dark-accent/20 hover:border-dark-accent'
                                    : 'bg-light-primary text-light-text border-light-accent/20 hover:border-light-accent'
                            ]">
                            <option value="">Случайная категория</option>
                            <option v-for="category in categories" :key="category" :value="category">
                                {{ category }}
                            </option>
                        </select>
                    </div>

                    <!-- Кнопка генерации -->
                    <button @click="generateExercise"
                        class="ml-4 px-6 py-2 rounded-lg font-medium transition-all duration-300 shadow-md transform hover:scale-105"
                        :class="[
                            themeStore.isDark
                                ? 'bg-dark-accent text-dark-text hover:bg-dark-accent/90'
                                : 'bg-light-accent text-light-text hover:bg-light-accent/90'
                        ]" :disabled="loading">
                        <template v-if="loading">
                            <span class="flex items-center">
                                <svg class="animate-spin -ml-1 mr-2 h-4 w-4" fill="none" viewBox="0 0 24 24">
                                    <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor"
                                        stroke-width="4" />
                                    <path class="opacity-75" fill="currentColor"
                                        d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4z" />
                                </svg>
                                Генерация...
                            </span>
                        </template>
                        <template v-else>
                            Следующее задание
                        </template>
                    </button>
                </div>
            </div>

            <!-- Карточка с упражнением -->
            <div v-if="exercise" class="p-6 rounded-lg shadow-lg transition-all duration-300 transform" :class="[
                themeStore.isDark ? 'bg-dark-secondary hover:shadow-dark-accent/20' : 'bg-light-secondary hover:shadow-light-accent/20',
                answerChecked ? (isCorrect ? 'scale-100' : 'scale-98') : ''
            ]">
                <!-- Определение -->
                <div class="mb-6">
                    <h3 class="text-xl font-semibold mb-3" :class="[
                        themeStore.isDark ? 'text-dark-text' : 'text-light-text'
                    ]">
                        Определение:
                    </h3>
                    <div class="space-y-2 p-4 rounded-lg" :class="[
                        themeStore.isDark ? 'bg-dark-primary/50' : 'bg-light-primary/50'
                    ]">
                        <!-- Английское определение -->
                        <p class="text-lg" :class="[
                            themeStore.isDark ? 'text-dark-text' : 'text-light-text'
                        ]">
                            {{ exercise.result.content.definition.en }}
                        </p>

                        <!-- Кнопка показа перевода -->
                        <button @click="toggleTranslation"
                            class="mt-2 px-4 py-2 text-sm rounded-lg transition-all duration-300 transform hover:scale-105"
                            :class="[
                                themeStore.isDark
                                    ? 'bg-dark-accent/20 text-dark-text hover:bg-dark-accent/30'
                                    : 'bg-light-accent/20 text-light-text hover:bg-light-accent/30'
                            ]">
                            {{ showTranslation ? 'Скрыть перевод' : 'Показать перевод' }}
                        </button>

                        <!-- Русский перевод -->
                        <p v-if="showTranslation" class="text-lg mt-2 transition-all duration-300" :class="[
                            themeStore.isDark ? 'text-dark-text/80' : 'text-light-text/80'
                        ]">
                            {{ exercise.result.content.definition.ru }}
                        </p>
                    </div>
                </div>

                <!-- Варианты ответов -->
                <div class="grid grid-cols-2 gap-4">
                    <button v-for="option in exercise.result.content.options" :key="option.id"
                        @click="selectAnswer(option.id)"
                        class="p-4 rounded-lg text-left transition-all duration-300 transform hover:scale-105 shadow-sm"
                        :class="[
                            selectedAnswer === option.id
                                ? [themeStore.isDark
                                    ? 'bg-dark-accent text-dark-text shadow-dark-accent/30'
                                    : 'bg-light-accent text-light-text shadow-light-accent/30']
                                : [themeStore.isDark
                                    ? 'bg-dark-primary text-dark-text hover:bg-dark-primary/80'
                                    : 'bg-light-primary text-light-text hover:bg-light-primary/80'],
                            // Показываем подсветку правильного/неправильного ответа только когда нужно
                            showCorrectAnswer && exercise.result.correct_answer === option.id
                                ? 'ring-2 ring-green-500'
                                : showCorrectAnswer && selectedAnswer === option.id
                                    ? 'ring-2 ring-red-500'
                                    : ''
                        ]" :disabled="loading || (answerChecked && !showCorrectAnswer)">
                        <div class="flex flex-col">
                            <span class="font-medium text-lg mb-1">{{ option.term }}</span>
                            <span class="text-sm opacity-75">{{ option.translation }}</span>
                        </div>
                    </button>
                </div>

                <!-- Результат и статистика -->
                <div v-if="answerChecked" class="mt-6 space-y-4">
                    <!-- Сообщение о результате -->
                    <div class="p-4 rounded-lg text-center transition-all duration-300" :class="[
                        isCorrect
                            ? 'bg-green-100 text-green-800'
                            : 'bg-red-100 text-red-800'
                    ]">
                        <p class="font-medium text-lg">
                            {{ isCorrect
                                ? 'Правильно!'
                                : attempts >= 2
                                    ? 'Неправильно. Посмотрите правильный ответ.'
                                    : 'Неправильно. Попробуйте еще раз.' }}
                        </p>
                    </div>

                    <div v-if="error" class="mt-4 p-4 rounded-lg bg-red-100 text-red-800">
                        {{ error }}
                    </div>
                </div>
            </div>
        </div>
    </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useThemeStore } from '@/stores/themeStore'
import { useAuthStore } from '@/stores/authStore'
import axios from 'axios'

const themeStore = useThemeStore()
const authStore = useAuthStore()

const loading = ref(false)
const categories = ref([])
const userProfile = ref(null)
const exercise = ref(null)
const selectedAnswer = ref(null)
const answerChecked = ref(false)
const isCorrect = ref(false)
const settings = ref({
    category: ''
})
const error = ref(null)
const showTranslation = ref(false)
const attempts = ref(0)
const showCorrectAnswer = ref(false)


// Получение списка категорий
async function fetchCategories() {
    try {
        const response = await axios.get('/api/v1/terms/categories')
        categories.value = response.data
    } catch (error) {
        console.error('Error fetching categories:', error)
    }
}

function toggleTranslation() {
    showTranslation.value = !showTranslation.value
}

// Получение профиля пользователя
async function fetchUserProfile() {
    try {
        const response = await axios.get('/api/v1/users/profile')
        userProfile.value = response.data
    } catch (error) {
        console.error('Error fetching user profile:', error)
    }
}

async function generateExercise() {
    loading.value = true
    try {
        const params = {
            task_type: 'term_definition',
            user_id: authStore.user?.id,
            params: {
                difficulty: userProfile.value?.current_level // Добавляем сложность из профиля
            }
        }

        // Добавляем категорию только если она выбрана
        if (settings.value.category) {
            params.params = {
                category: settings.value.category
            }
        }

        const response = await axios.post('/api/v1/tasks/generate/term-definition', params)
        exercise.value = response.data
        selectedAnswer.value = null
        answerChecked.value = false
    } catch (err) {
        error.value = 'Не удалось загрузить задание. Попробуйте еще раз.'
        console.error('Error generating exercise:', err)
    } finally {
        loading.value = false
    }
}

async function checkAnswer() {
    if (selectedAnswer.value === null) return

    answerChecked.value = true
    loading.value = true

    try {
        const response = await axios.post('/api/v1/tasks/generate/term-definition/validate', {
            task_id: exercise.value.task_id,
            term_id: selectedAnswer.value,
            correct_term_id: exercise.value.result.correct_answer
        })

        isCorrect.value = response.data.is_correct
        attempts.value++

        if (isCorrect.value || attempts.value >= 2) {
            // Показываем правильный ответ только после 2 попыток или при правильном ответе
            showCorrectAnswer.value = true
            if (isCorrect.value) {
                // Генерируем новое задание только при правильном ответе
                setTimeout(() => {
                    answerChecked.value = false
                    selectedAnswer.value = null
                    showCorrectAnswer.value = false
                    attempts.value = 0
                    showTranslation.value = false
                    generateExercise()
                }, 1500)
            }
        }
    } catch (error) {
        console.error('Error validating answer:', error)
    } finally {
        loading.value = false
    }
}

// Автоматически проверяем ответ при выборе
function selectAnswer(id) {
    if (answerChecked.value || loading.value) return
    selectedAnswer.value = id
    checkAnswer()
}

function formatDifficulty(difficulty) {
    const difficulties = {
        'beginner': 'Начальный',
        'basic': 'Базовый',
        'intermediate': 'Средний',
        'advanced': 'Продвинутый'
    }
    return difficulties[difficulty] || difficulty
}

onMounted(async () => {
    await Promise.all([
        fetchCategories(),
        fetchUserProfile()
    ])
    generateExercise()
})
</script>

<style scoped>
.container {
    min-height: calc(100vh - 4rem);
}

/* Добавляем плавные переходы для всех трансформаций */
.transition-all {
    transition-property: all;
    transition-timing-function: cubic-bezier(0.4, 0, 0.2, 1);
    transition-duration: 300ms;
}
</style>