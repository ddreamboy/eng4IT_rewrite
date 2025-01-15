<!-- src/views/WordMatchingExercise.vue -->
<template>
    <div class="container mx-auto px-4 py-8">
        <!-- Заголовок и статистика -->
        <header class="mb-8">
            <div class="flex justify-between items-center mb-4">
                <h1 class="text-2xl font-bold" :class="[themeStore.isDark ? 'text-dark-text' : 'text-light-text']">
                    Word Matching - Level {{ currentLevel }}
                </h1>
                <div class="flex items-center space-x-4">
                    <!-- Жизни -->
                    <div class="flex items-center space-x-1">
                        <Heart v-for="life in lives" :key="life"
                            :class="[themeStore.isDark ? 'text-dark-accent' : 'text-light-accent']" class="w-6 h-6"
                            :fill="'currentColor'" />
                        <Heart v-for="lost in 3 - lives" :key="'lost' + lost" class="w-6 h-6 opacity-30" />
                    </div>
                    <!-- Счет -->
                    <div class="text-lg font-bold" :class="[themeStore.isDark ? 'text-dark-text' : 'text-light-text']">
                        {{ score }}
                    </div>
                </div>
            </div>

            <!-- Прогресс уровня -->
            <div class="relative h-2 rounded-full overflow-hidden"
                :class="[themeStore.isDark ? 'bg-dark-primary' : 'bg-light-primary']">
                <div class="absolute left-0 top-0 h-full transition-all duration-300 rounded-full"
                    :style="{ width: `${levelProgress}%` }"
                    :class="[themeStore.isDark ? 'bg-dark-accent' : 'bg-light-accent']"></div>
            </div>
        </header>


        <!-- Основная игровая область -->
        <div class="grid grid-cols-2 gap-8 max-w-4xl mx-auto">
            <!-- Английские слова -->
            <div class="space-y-4">
                <TransitionGroup name="word-card">
                    <template v-for="(batch, batchIndex) in englishWordBatches" :key="batchIndex">
                        <div v-if="currentBatch === batchIndex" class="grid grid-cols-1 gap-4">
                            <button v-for="word in batch" :key="word.id" @click="selectWord(word, 'en')"
                                :data-word-id="word.id"
                                class="h-24 p-4 rounded-lg text-center transition-all duration-300 relative flex items-center justify-center"
                                :class="[
                                    // Базовые стили
                                    themeStore.isDark ? 'bg-dark-secondary' : 'bg-light-secondary',
                                    // Стили выделения
                                    selectedEnWord?.id === word.id ? 'ring-4 ring-green-500 animate-pulse' : '',
                                    // Стили для завершенных пар
                                    completedPairs[word.id]
                                        ? [
                                            themeStore.isDark ? 'opacity-50 bg-green-800' : 'opacity-50 bg-green-200',
                                            'cursor-not-allowed',
                                        ]
                                        : 'hover:scale-105',
                                ]">
                                <AutoResizingText :text="word.text" />
                                <!-- Анимированная обводка для правильной пары -->
                                <div v-if="completedPairs[word.id]"
                                    class="absolute inset-0 rounded-lg border-4 border-green-500 animate-success"></div>
                            </button>
                        </div>
                    </template>
                </TransitionGroup>
            </div>

            <!-- Русские слова -->
            <div class="space-y-4">
                <TransitionGroup name="word-card">
                    <template v-for="(batch, batchIndex) in russianWordBatches" :key="batchIndex">
                        <div v-if="currentBatch === batchIndex" class="grid grid-cols-1 gap-4">
                            <button v-for="word in batch" :key="word.id" @click="selectWord(word, 'ru')"
                                :data-word-id="word.id"
                                class="h-24 p-4 rounded-lg text-center transition-all duration-300 relative flex items-center justify-center"
                                :class="[
                                    // Базовые стили
                                    themeStore.isDark ? 'bg-dark-secondary' : 'bg-light-secondary',
                                    // Стили выделения
                                    selectedRuWord?.id === word.id ? 'ring-4 ring-green-500 animate-pulse' : '',
                                    // Стили для завершенных пар
                                    completedPairs[word.id]
                                        ? [
                                            themeStore.isDark ? 'opacity-50 bg-green-800' : 'opacity-50 bg-green-200',
                                            'cursor-not-allowed',
                                        ]
                                        : 'hover:scale-105',
                                ]">
                                <AutoResizingText :text="word.text" />
                                <!-- Анимированная обводка для правильной пары -->
                                <div v-if="completedPairs[word.id]"
                                    class="absolute inset-0 rounded-lg border-4 border-green-500 animate-success"></div>
                            </button>
                        </div>
                    </template>
                </TransitionGroup>
            </div>
        </div>

        <!-- Модалка результатов уровня -->
        <TransitionRoot appear :show="showLevelComplete" as="template">
            <Dialog as="div" @close="proceedToNextLevel" class="relative z-50">
                <TransitionChild as="template" enter="duration-300 ease-out" enter-from="opacity-0"
                    enter-to="opacity-100" leave="duration-200 ease-in" leave-from="opacity-100" leave-to="opacity-0">
                    <div class="fixed inset-0 bg-black/50" />
                </TransitionChild>

                <div class="fixed inset-0 overflow-y-auto">
                    <div class="flex min-h-full items-center justify-center p-4">
                        <TransitionChild as="template" enter="duration-300 ease-out" enter-from="opacity-0 scale-95"
                            enter-to="opacity-100 scale-100" leave="duration-200 ease-in"
                            leave-from="opacity-100 scale-100" leave-to="opacity-0 scale-95">
                            <DialogPanel class="w-full max-w-md p-6 rounded-lg shadow-xl transition-all"
                                :class="[themeStore.isDark ? 'bg-dark-secondary' : 'bg-light-secondary']">
                                <DialogTitle as="h3" class="text-2xl font-bold mb-4"
                                    :class="[themeStore.isDark ? 'text-dark-text' : 'text-light-text']">
                                    Level {{ currentLevel }} Complete!
                                </DialogTitle>

                                <div class="mb-6 space-y-4">
                                    <!-- Статистика уровня -->
                                    <div class="space-y-2">
                                        <div class="flex justify-between items-center">
                                            <span
                                                :class="[themeStore.isDark ? 'text-dark-text/70' : 'text-light-text/70']">x{{
                                                    levelStats.multipliers.level.toFixed(2) }}</span>
                                        </div>
                                    </div>
                                </div>

                                <div class="flex justify-end">
                                    <button @click="proceedToNextLevel"
                                        class="px-4 py-2 rounded-lg font-medium transition-all duration-300" :class="[
                                            themeStore.isDark
                                                ? 'bg-dark-accent text-dark-text hover:bg-dark-accent/90'
                                                : 'bg-light-accent text-light-text hover:bg-light-accent/90',
                                        ]">
                                        Next Level
                                    </button>
                                </div>
                            </DialogPanel>
                        </TransitionChild>
                    </div>
                </div>
            </Dialog>
        </TransitionRoot>

        <!-- Модалка окончания игры -->
        <TransitionRoot appear :show="showGameOver" as="template">
            <Dialog as="div" @close="restartGame" class="relative z-50">
                <TransitionChild as="template" enter="duration-300 ease-out" enter-from="opacity-0"
                    enter-to="opacity-100" leave="duration-200 ease-in" leave-from="opacity-100" leave-to="opacity-0">
                    <div class="fixed inset-0 bg-black/50" />
                </TransitionChild>

                <div class="fixed inset-0 overflow-y-auto">
                    <div class="flex min-h-full items-center justify-center p-4">
                        <TransitionChild as="template" enter="duration-300 ease-out" enter-from="opacity-0 scale-95"
                            enter-to="opacity-100 scale-100" leave="duration-200 ease-in"
                            leave-from="opacity-100 scale-100" leave-to="opacity-0 scale-95">
                            <DialogPanel class="w-full max-w-md p-6 rounded-lg shadow-xl transition-all"
                                :class="[themeStore.isDark ? 'bg-dark-secondary' : 'bg-light-secondary']">
                                <DialogTitle as="h3" class="text-2xl font-bold mb-4"
                                    :class="[themeStore.isDark ? 'text-dark-text' : 'text-light-text']">
                                    Game Over!
                                </DialogTitle>

                                <div class="mb-6 space-y-4">
                                    <div class="text-center">
                                        <p class="text-4xl font-bold mb-2"
                                            :class="[themeStore.isDark ? 'text-dark-text' : 'text-light-text']">
                                            {{ score }}
                                        </p>
                                        <p class="text-sm"
                                            :class="[themeStore.isDark ? 'text-dark-text/70' : 'text-light-text/70']">
                                            Final Score
                                        </p>
                                    </div>

                                    <!-- Общая статистика -->
                                    <div class="space-y-2">
                                        <div class="flex justify-between items-center">
                                            <span
                                                :class="[themeStore.isDark ? 'text-dark-text/70' : 'text-light-text/70']">Levels
                                                Completed:</span>
                                            <span class="font-bold"
                                                :class="[themeStore.isDark ? 'text-dark-text' : 'text-light-text']">{{
                                                    currentLevel - 1 }}</span>
                                        </div>
                                        <div class="flex justify-between items-center">
                                            <span
                                                :class="[themeStore.isDark ? 'text-dark-text/70' : 'text-light-text/70']">Words
                                                Matched:</span>
                                            <span class="font-bold"
                                                :class="[themeStore.isDark ? 'text-dark-text' : 'text-light-text']">{{
                                                    totalWordsMatched }}</span>
                                        </div>
                                        <div class="flex justify-between items-center">
                                            <span
                                                :class="[themeStore.isDark ? 'text-dark-text/70' : 'text-light-text/70']">Total
                                                Time:</span>
                                            <span class="font-bold"
                                                :class="[themeStore.isDark ? 'text-dark-text' : 'text-light-text']">{{
                                                    formatTime(totalTime) }}</span>
                                        </div>
                                    </div>
                                </div>

                                <div class="flex justify-end space-x-4">
                                    <button @click="goHome"
                                        class="px-4 py-2 rounded-lg font-medium transition-all duration-300" :class="[
                                            themeStore.isDark
                                                ? 'bg-dark-primary text-dark-text hover:bg-dark-primary/90'
                                                : 'bg-light-primary text-light-text hover:bg-light-primary/90',
                                        ]">
                                        Home
                                    </button>
                                    <button @click="restartGame"
                                        class="px-4 py-2 rounded-lg font-medium transition-all duration-300" :class="[
                                            themeStore.isDark
                                                ? 'bg-dark-accent text-dark-text hover:bg-dark-accent/90'
                                                : 'bg-light-accent text-light-text hover:bg-light-accent/90',
                                        ]">
                                        Play Again
                                    </button>
                                </div>
                            </DialogPanel>
                        </TransitionChild>
                    </div>
                </div>
            </Dialog>
        </TransitionRoot>
    </div>
</template>

<script setup>
import { ref, computed, onMounted, watch } from 'vue'
import { useRouter } from 'vue-router'
import { useThemeStore } from '@/stores/themeStore'
import { useAuthStore } from '@/stores/authStore'
import { Heart } from 'lucide-vue-next'
import { TransitionRoot, TransitionChild, Dialog, DialogPanel, DialogTitle } from '@headlessui/vue'
import AutoResizingText from '@/components/AutoResizingText.vue'
import axios from 'axios'

// Добавляем новые состояния для батчей
const currentBatch = ref(0)
const batchSize = 5

const router = useRouter()
const themeStore = useThemeStore()
const authStore = useAuthStore()

// Игровое состояние
const currentLevel = ref(1)
const lives = ref(3)
const score = ref(0)
const gameStartTime = ref(Date.now())
const levelStartTime = ref(Date.now())
const showLevelComplete = ref(false)
const showGameOver = ref(false)
const loading = ref(false)
const userProfile = ref(null)

// Игровые данные
const currentEnglishWords = ref([])
const currentRussianWords = ref([])
const completedPairs = ref({})
const wrongAttempts = ref([])
const selectedEnWord = ref(null)
const selectedRuWord = ref(null)

// Разбиваем слова на батчи
const englishWordBatches = computed(() => {
    return chunk(currentEnglishWords.value, batchSize)
})

const russianWordBatches = computed(() => {
    return chunk(currentRussianWords.value, batchSize)
})

// Функция для разбивки массива на батчи
function chunk(array, size) {
    const chunks = []
    for (let i = 0; i < array.length; i += size) {
        chunks.push(array.slice(i, i + size))
    }
    return chunks
}
// Прогресс уровня
const levelProgress = computed(() => {
    const total = getPairsForLevel(currentLevel.value)
    const completed = Object.keys(completedPairs.value).length
    return (completed / total) * 100
})

// Статистика уровня
const levelStats = ref({
    timeSpent: 0,
    accuracy: 100,
    score: 0,
    multipliers: {
        time: 1,
        accuracy: 1,
        level: 1,
    },
})

// Количество пар слов для каждого уровня
function getPairsForLevel(level) {
    const pairs = {
        1: 10,
        2: 20,
        3: 35,
        4: 45,
        5: 50,
    }
    return pairs[level] || 50
}

// Загрузка профиля пользователя
async function fetchUserProfile() {
    try {
        const response = await axios.get('/api/v1/users/profile')
        userProfile.value = response.data
    } catch (error) {
        console.error('Error fetching user profile:', error)
    }
}

// Загрузка слов для уровня
// Модифицированная функция загрузки слов в WordMatchingExercise.vue
async function loadWords() {
    loading.value = true
    try {
        const request_params = {
            task_type: 'word_matching',
            user_id: authStore.user?.id,
            params: {
                pairs_count: getPairsForLevel(currentLevel.value),
                difficulty: userProfile.value?.current_level || 'basic',
            },
        }

        const response = await axios.post('/api/v1/tasks/generate/word-matching', request_params)
        const data = response.data.result.content

        console.log('Loaded words', data)

        // Разбиваем на батчи сразу
        let batches = []
        for (let i = 0; i < data.originals.length; i += batchSize) {
            const batchOriginals = data.originals.slice(i, i + batchSize)
            const batchTranslations = data.translations.slice(i, i + batchSize)
            batches.push({
                originals: batchOriginals,
                translations: shuffleArray([...batchTranslations]) // Перемешиваем только переводы в батче
            })
        }

        // Теперь формируем финальные массивы
        currentEnglishWords.value = batches.map(batch => batch.originals).flat()
        currentRussianWords.value = batches.map(batch => batch.translations).flat()

        // Сбрасываем состояние
        currentBatch.value = 0
        completedPairs.value = {}
        wrongAttempts.value = []
        levelStartTime.value = Date.now()

        return response.data
    } catch (error) {
        console.error('Error loading words:', error)
        throw error
    } finally {
        loading.value = false
    }
}

// Перемешивание массива
function shuffleArray(array) {
    for (let i = array.length - 1; i > 0; i--) {
        const j = Math.floor(Math.random() * (i + 1))
            ;[array[i], array[j]] = [array[j], array[i]]
    }
    return array
}

// Выбор слова
async function selectWord(word, type) {
    if (completedPairs.value[word.id]) return

    if (type === 'en') {
        selectedEnWord.value = selectedEnWord.value?.id === word.id ? null : word
    } else {
        selectedRuWord.value = selectedRuWord.value?.id === word.id ? null : word
    }

    // Если выбраны оба слова, проверяем пару
    if (selectedEnWord.value && selectedRuWord.value) {
        await checkPair()
    }
}

// Проверка выбранной пары
// Модифицированная функция проверки пары
async function checkPair() {
    // Проверяем соответствие ID
    const isCorrect = selectedEnWord.value.id === selectedRuWord.value.id

    if (isCorrect) {
        completedPairs.value[selectedEnWord.value.id] = true

        // Проверяем завершение текущего батча
        const currentBatchWords = englishWordBatches.value[currentBatch.value]
        const allBatchWordsCompleted = currentBatchWords.every(word => completedPairs.value[word.id])

        if (allBatchWordsCompleted) {
            if (currentBatch.value < englishWordBatches.value.length - 1) {
                setTimeout(() => {
                    currentBatch.value++
                }, 1000)
            }
        }

        // Проверяем завершение уровня
        if (Object.keys(completedPairs.value).length === getPairsForLevel(currentLevel.value)) {
            await validateLevel()
            showLevelComplete.value = true
        }
    } else {
        // Записываем неправильную попытку
        wrongAttempts.value.push({
            word_id: selectedEnWord.value.id,
            wrong_translation_id: selectedRuWord.value.id,
            timestamp: Date.now(),
        })

        lives.value--
        if (lives.value <= 0) {
            await validateLevel()
            showGameOver.value = true
        }
    }

    // Сбрасываем выбор
    selectedEnWord.value = null
    selectedRuWord.value = null
}

// Валидация уровня
async function validateLevel() {
    const timeSpent = Math.floor((Date.now() - levelStartTime.value) / 1000)
    try {
        const validate_request = {
            task_id: `word_matching_${currentLevel.value}`,
            pairs: Object.fromEntries(
                Object.entries(completedPairs.value)
                    .map(([wordId, _]) => {
                        const translation = currentRussianWords.value.find((word) => word.id === parseInt(wordId))?.text;
                        return translation ? [parseInt(wordId), translation] : null;
                    })
                    .filter((entry) => entry !== null)
            ),
            correct_pairs: Object.fromEntries(
                currentEnglishWords.value.map((word) => [
                    word.id,
                    currentRussianWords.value.find((w) => w.id === word.id)?.text || '',
                ])
            ),
            wrong_attempts: [...wrongAttempts.value],
            time_spent: timeSpent,
            level: currentLevel.value,
            lives: lives.value,
            current_score: score.value,
            user_id: authStore.user?.id, // Добавляем user_id
        };

        console.log('Validating level:', validate_request)

        const response = await axios.post('/api/v1/tasks/generate/word-matching/validate', validate_request)

        // Обновляем статистику уровня
        levelStats.value = {
            timeSpent,
            accuracy: response.data.statistics.accuracy,
            score: response.data.score_data.final_score,
            multipliers: response.data.score_data,
        }

        score.value += response.data.score_data.final_score
    } catch (error) {
        console.error('Error validating level:', error)
    }
}

// Переход к следующему уровню
async function proceedToNextLevel() {
    if (currentLevel.value < 5) {
        currentLevel.value++
        showLevelComplete.value = false
        await loadWords()
    } else {
        showGameOver.value = true
    }
}

// Перезапуск игры
async function restartGame() {
    currentLevel.value = 1
    lives.value = 3
    score.value = 0
    gameStartTime.value = Date.now()
    showGameOver.value = false
    await loadWords()
}

// Возврат на главную
function goHome() {
    router.push('/')
}

// Форматирование времени
function formatTime(seconds) {
    const minutes = Math.floor(seconds / 60)
    const remainingSeconds = seconds % 60
    return `${minutes}:${remainingSeconds.toString().padStart(2, '0')}`
}

// Вычисляемые свойства для статистики
const totalWordsMatched = computed(() => Object.keys(completedPairs.value).length)

const totalTime = computed(() => Math.floor((Date.now() - gameStartTime.value) / 1000))

// Инициализация
onMounted(async () => {
    await fetchUserProfile()
    await loadWords()
})
</script>

<style scoped>
.word-card-enter-active,
.word-card-leave-active {
    transition: all 0.3s ease;
}

.word-card-enter-from,
.word-card-leave-to {
    opacity: 0;
    transform: translateY(30px);
}

@keyframes success-pulse {
    0% {
        opacity: 1;
        transform: scale(1);
    }

    50% {
        opacity: 0.5;
        transform: scale(1.05);
    }

    100% {
        opacity: 1;
        transform: scale(1);
    }
}

.animate-success {
    animation: success-pulse 1s ease-in-out;
}

.animate-pulse {
    animation: pulse 2s cubic-bezier(0.4, 0, 0.6, 1) infinite;
}

@keyframes pulse {

    0%,
    100% {
        opacity: 1;
    }

    50% {
        opacity: .7;
    }
}
</style>
