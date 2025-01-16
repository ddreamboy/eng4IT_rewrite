<!-- src/views/WordTranslationExercise.vue -->
<script setup>
import { ref, onMounted, computed, watch } from 'vue'
import { useThemeStore } from '@/stores/themeStore'
import { useAuthStore } from '@/stores/authStore'
import axios from 'axios'

const themeStore = useThemeStore()
const authStore = useAuthStore()

// Состояния компонента
const loading = ref(false)
const wordTypes = ref([
    { value: 'NOUN', label: 'Существительное' },
    { value: 'VERB', label: 'Глагол' },
    { value: 'ADJECTIVE', label: 'Прилагательное' },
    { value: 'ADVERB', label: 'Наречие' },
    { value: 'COMMON_PHRASE', label: 'Фраза' }
])
const userProfile = ref(null)
const exercise = ref(null)
const selectedAnswer = ref(null)
const answerChecked = ref(false)
const isCorrect = ref(false)
const settings = ref({
    wordType: '',
})
const showContext = ref(false)
const attempts = ref(0)
const showCorrectAnswer = ref(false)

// Показываем кнопку "Следующее задание" 
const showNextButton = computed(
    () => (attempts.value >= 2 && showCorrectAnswer.value)
)

// Следим за изменением типа слова
watch(
    () => settings.value.wordType,
    () => {
        generateExercise()
    }
)

// Получение профиля пользователя
async function fetchUserProfile() {
    try {
        const response = await axios.get('/api/v1/users/profile')
        userProfile.value = response.data
    } catch (error) {
        console.error('Error fetching user profile:', error)
    }
}

// Переключение видимости контекста
function toggleContext() {
    showContext.value = !showContext.value
}

// Генерация упражнения
async function generateExercise() {
    loading.value = true
    try {
        const params = {
            difficulty: userProfile.value?.current_level || 'basic',
        }

        // Добавляем тип слова, если выбран
        if (settings.value.wordType) {
            params.word_type = settings.value.wordType
        }

        const request_params = {
            task_type: 'word_translation',
            user_id: authStore.user?.id,
            params: params,
        }
        console.log('User ID:', authStore.user?.id)
        console.log('Request params:', request_params)

        const response = await axios.post('/api/v1/tasks/generate/word-translation', request_params)
        exercise.value = response.data

        // Сбрасываем состояние
        selectedAnswer.value = null
        answerChecked.value = false
        showCorrectAnswer.value = false
        isCorrect.value = false
        attempts.value = 0
        showContext.value = false
    } catch (err) {
        console.error('Error generating exercise:', err)
    } finally {
        loading.value = false
    }
}

// Проверка ответа
async function checkAnswer() {
    if (selectedAnswer.value === null) return

    answerChecked.value = true
    loading.value = true

    try {
        console.log('Validating answer:', selectedAnswer.value)
        console.log('Exercise:', exercise.value.task_id)
        console.log('User ID:', authStore.user?.id)
        console.log('Word ID:', exercise.value.result.word_id,)
        const response = await axios.post('/api/v1/tasks/generate/word-translation/validate', {
            task_id: exercise.value.task_id,
            answer: selectedAnswer.value,
            word_id: exercise.value.result.word_id,
            user_id: authStore.user?.id,
        })

        console.log('Answer validation response:', response.data)

        isCorrect.value = response.data.is_correct
        attempts.value++

        // Показываем правильный ответ 
        if (isCorrect.value || attempts.value >= 2) {
            showCorrectAnswer.value = true
            if (isCorrect.value) {
                // Автоматически генерируем новое задание через задержку
                setTimeout(() => {
                    generateExercise()
                }, 500)
            }
        }
    } catch (error) {
        console.error('Error validating answer:', error)
    } finally {
        loading.value = false
    }
}

// Определяем, можно ли взаимодействовать с кнопкой
function isOptionDisabled(option) {
    return loading.value || isCorrect.value || (showCorrectAnswer.value && attempts.value >= 2)
}

// Обработка выбора ответа
function selectAnswer(option) {
    if (isOptionDisabled()) return
    selectedAnswer.value = option
    checkAnswer()
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
                Перевод слова
            </h1>
            <p class="text-sm" :class="[themeStore.isDark ? 'text-dark-text/70' : 'text-light-text/70']">
                Выберите правильный перевод для указанного слова
            </p>
        </header>

        <div class="max-w-2xl mx-auto">
            <!-- Настройки -->
            <div class="mb-8 p-6 rounded-lg shadow-lg transition-all duration-300" :class="[
                themeStore.isDark
                    ? 'bg-dark-secondary hover:shadow-dark-accent/20'
                    : 'bg-light-secondary hover:shadow-light-accent/20',
            ]">
                <div class="flex items-center justify-between">
                    <!-- Выбор типа слова -->
                    <div class="flex-1 max-w-xs">
                        <label class="block text-sm font-medium mb-2"
                            :class="[themeStore.isDark ? 'text-dark-text' : 'text-light-text']">
                            Тип слова (необязательно)
                        </label>
                        <select v-model="settings.wordType"
                            class="w-full px-4 py-2 rounded-lg transition-all duration-300 shadow-sm" :class="[
                                themeStore.isDark
                                    ? 'bg-dark-primary text-dark-text border-dark-accent/20 hover:border-dark-accent'
                                    : 'bg-light-primary text-light-text border-light-accent/20 hover:border-light-accent',
                            ]">
                            <option value="">Случайный тип</option>
                            <option v-for="type in wordTypes" :key="type.value" :value="type.value">
                                {{ type.label }}
                            </option>
                        </select>
                    </div>

                    <!-- Кнопка генерации -->
                    <button v-if="showNextButton" @click="generateExercise"
                        class="ml-4 px-6 py-2 rounded-lg font-medium transition-all duration-300 shadow-md transform hover:scale-105"
                        :class="[
                            themeStore.isDark
                                ? 'bg-dark-accent text-dark-text hover:bg-dark-accent/90'
                                : 'bg-light-accent text-light-text hover:bg-light-accent/90',
                        ]">
                        Следующее задание
                    </button>
                </div>
            </div>

            <!-- Карточка с упражнением -->
            <div v-if="exercise" class="p-6 rounded-lg shadow-lg transition-all duration-300" :class="[
                themeStore.isDark
                    ? 'bg-dark-secondary hover:shadow-dark-accent/20'
                    : 'bg-light-secondary hover:shadow-light-accent/20',
            ]">
                <!-- Слово -->
                <div class="mb-6">
                    <h3 class="text-xl font-semibold mb-3"
                        :class="[themeStore.isDark ? 'text-dark-text' : 'text-light-text']">
                        Слово:
                    </h3>
                    <div class="space-y-2 p-4 rounded-lg"
                        :class="[themeStore.isDark ? 'bg-dark-primary/50' : 'bg-light-primary/50']">
                        <!-- Английское слово -->
                        <p class="text-lg" :class="[themeStore.isDark ? 'text-dark-text' : 'text-light-text']">
                            {{ exercise.result.content.word }}
                        </p>

                        <p class="italic" :class="[themeStore.isDark ? 'text-dark-text/80' : 'text-light-text/80']">
                            {{ exercise.result.content.context }}
                        </p>

                        <!-- Контекст -->
                        <button v-if="exercise.result.content.context" @click="toggleContext"
                            class="mt-2 px-4 py-2 text-sm rounded-lg transition-all duration-300 transform hover:scale-105"
                            :class="[
                                themeStore.isDark
                                    ? 'bg-dark-accent/20 text-dark-text hover:bg-dark-accent/30'
                                    : 'bg-light-accent/20 text-light-text hover:bg-light-accent/30',
                            ]">
                            {{ showContext ? 'Скрыть контекст' : 'Показать перевод контекста' }}
                        </button>

                        <!-- Контекст использования -->
                        <div v-if="showContext && exercise.result.content.context"
                            class="mt-2 transition-all duration-300">
                            <p class="italic mt-1"
                                :class="[themeStore.isDark ? 'text-dark-text/60' : 'text-light-text/60']">
                                {{ exercise.result.content.context_translation }}
                            </p>
                        </div>
                    </div>
                </div>

                <!-- Варианты перевода -->
                <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
                    <button v-for="option in exercise.result.content.options" :key="option"
                        @click="selectAnswer(option)" :disabled="isOptionDisabled(option)"
                        class="p-4 rounded-lg text-left transition-all duration-300 transform hover:scale-105 shadow-sm relative"
                        :class="[
                            themeStore.isDark
                                ? 'bg-dark-primary text-dark-text hover:bg-dark-primary/80'
                                : 'bg-light-primary text-light-text hover:bg-light-primary/80',
                            selectedAnswer === option && !showCorrectAnswer ? 'ring-2 ring-blue-500' : '',
                            showCorrectAnswer && exercise.result.correct_answer === option
                                ? 'ring-2 ring-green-500'
                                : '',
                            showCorrectAnswer &&
                                selectedAnswer === option &&
                                exercise.result.correct_answer !== option
                                ? 'ring-2 ring-red-500'
                                : '',
                            isOptionDisabled(option) ? 'opacity-75 cursor-not-allowed hover:scale-100' : '',
                        ]">
                        {{ option }}
                    </button>
                </div>

                <!-- Сообщение о неправильном ответе -->
                <div v-if="attempts === 1 && !isCorrect"
                    class="mt-4 p-4 rounded-lg transition-all duration-300 animate-fade-in"
                    :class="[themeStore.isDark ? 'bg-red-900/20 text-red-200' : 'bg-red-50 text-red-800']">
                    <p>Попробуй еще раз</p>
                </div>
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

@keyframes fadeIn {
    from {
        opacity: 0;
    }

    to {
        opacity: 1;
    }
}

.animate-fade-in {
    animation: fadeIn 0.1s ease-out;
}
</style>