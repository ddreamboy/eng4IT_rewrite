<!-- src/views/WordMatchingExercise.vue -->
<template>
    <div class="container mx-auto px-4 py-8">
        <!-- Заголовок и статистика -->
        <header class="mb-8">
            <div class="flex justify-between items-center mb-4">
                <h1 class="text-2xl font-bold" :class="[
                    themeStore.isDark ? 'text-dark-text' : 'text-light-text'
                ]">
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
                    <div class="text-lg font-bold" :class="[
                        themeStore.isDark ? 'text-dark-text' : 'text-light-text'
                    ]">
                        {{ score }}
                    </div>
                </div>
            </div>

            <!-- Прогресс уровня -->
            <div class="relative h-2 rounded-full overflow-hidden" :class="[
                themeStore.isDark ? 'bg-dark-primary' : 'bg-light-primary'
            ]">
                <div class="absolute left-0 top-0 h-full transition-all duration-300 rounded-full"
                    :style="{ width: `${levelProgress}%` }" :class="[
                        themeStore.isDark ? 'bg-dark-accent' : 'bg-light-accent'
                    ]">
                </div>
            </div>
        </header>

        <!-- Основная игровая область -->
        <div class="grid grid-cols-2 gap-4 md:gap-6">
            <!-- Английские слова -->
            <div class="space-y-2 md:space-y-4">
                <TransitionGroup name="word-card">
                    <button v-for="word in currentEnglishWords" :key="word.id" @click="selectWord(word, 'en')"
                        :data-word-id="word.id"
                        class="w-full p-4 rounded-lg text-center transition-all duration-300 transform hover:scale-105"
                        :class="[
                            // Базовые стили
                            themeStore.isDark ? 'bg-dark-secondary' : 'bg-light-secondary',
                            // Стили выделения
                            selectedEnWord?.id === word.id ? 'ring-2 ring-blue-500' : '',
                            // Стили для завершенных пар
                            completedPairs[word.id] ? [
                                themeStore.isDark ? 'opacity-50 bg-green-800' : 'opacity-50 bg-green-200'
                            ] : ''
                        ]">
                        <AutoResizingText :text="word.text" />
                    </button>
                </TransitionGroup>
            </div>

            <!-- Русские слова -->
            <div class="space-y-2 md:space-y-4">
                <TransitionGroup name="word-card">
                    <button v-for="word in currentRussianWords" :key="word.id" @click="selectWord(word, 'ru')"
                        :data-word-id="word.id"
                        class="w-full p-4 rounded-lg text-center transition-all duration-300 transform hover:scale-105"
                        :class="[
                            // Базовые стили
                            themeStore.isDark ? 'bg-dark-secondary' : 'bg-light-secondary',
                            // Стили выделения
                            selectedRuWord?.id === word.id ? 'ring-2 ring-blue-500' : '',
                            // Стили для завершенных пар
                            completedPairs[word.id] ? [
                                themeStore.isDark ? 'opacity-50 bg-green-800' : 'opacity-50 bg-green-200'
                            ] : ''
                        ]">
                        <AutoResizingText :text="word.text" />
                    </button>
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
                            <DialogPanel class="w-full max-w-md p-6 rounded-lg shadow-xl transition-all" :class="[
                                themeStore.isDark ? 'bg-dark-secondary' : 'bg-light-secondary'
                            ]">
                                <DialogTitle as="h3" class="text-2xl font-bold mb-4" :class="[
                                    themeStore.isDark ? 'text-dark-text' : 'text-light-text'
                                ]">
                                    Level {{ currentLevel }} Complete!
                                </DialogTitle>

                                <div class="mb-6 space-y-4">
                                    <!-- Статистика уровня -->
                                    <div class="space-y-2">
                                        <div class="flex justify-between items-center">
                                            <span :class="[
                                                themeStore.isDark ? 'text-dark-text/70' : 'text-light-text/70'
                                            ]">x{{ levelStats.multipliers.level.toFixed(2) }}</span>
                                        </div>
                                    </div>
                                </div>

                                <div class="flex justify-end">
                                    <button @click="proceedToNextLevel"
                                        class="px-4 py-2 rounded-lg font-medium transition-all duration-300" :class="[
                                            themeStore.isDark
                                                ? 'bg-dark-accent text-dark-text hover:bg-dark-accent/90'
                                                : 'bg-light-accent text-light-text hover:bg-light-accent/90'
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
                            <DialogPanel class="w-full max-w-md p-6 rounded-lg shadow-xl transition-all" :class="[
                                themeStore.isDark ? 'bg-dark-secondary' : 'bg-light-secondary'
                            ]">
                                <DialogTitle as="h3" class="text-2xl font-bold mb-4" :class="[
                                    themeStore.isDark ? 'text-dark-text' : 'text-light-text'
                                ]">
                                    Game Over!
                                </DialogTitle>

                                <div class="mb-6 space-y-4">
                                    <div class="text-center">
                                        <p class="text-4xl font-bold mb-2" :class="[
                                            themeStore.isDark ? 'text-dark-text' : 'text-light-text'
                                        ]">
                                            {{ score }}
                                        </p>
                                        <p class="text-sm" :class="[
                                            themeStore.isDark ? 'text-dark-text/70' : 'text-light-text/70'
                                        ]">
                                            Final Score
                                        </p>
                                    </div>

                                    <!-- Общая статистика -->
                                    <div class="space-y-2">
                                        <div class="flex justify-between items-center">
                                            <span :class="[
                                                themeStore.isDark ? 'text-dark-text/70' : 'text-light-text/70'
                                            ]">Levels Completed:</span>
                                            <span class="font-bold" :class="[
                                                themeStore.isDark ? 'text-dark-text' : 'text-light-text'
                                            ]">{{ currentLevel - 1 }}</span>
                                        </div>
                                        <div class="flex justify-between items-center">
                                            <span :class="[
                                                themeStore.isDark ? 'text-dark-text/70' : 'text-light-text/70'
                                            ]">Words Matched:</span>
                                            <span class="font-bold" :class="[
                                                themeStore.isDark ? 'text-dark-text' : 'text-light-text'
                                            ]">{{ totalWordsMatched }}</span>
                                        </div>
                                        <div class="flex justify-between items-center">
                                            <span :class="[
                                                themeStore.isDark ? 'text-dark-text/70' : 'text-light-text/70'
                                            ]">Total Time:</span>
                                            <span class="font-bold" :class="[
                                                themeStore.isDark ? 'text-dark-text' : 'text-light-text'
                                            ]">{{ formatTime(totalTime) }}</span>
                                        </div>
                                    </div>
                                </div>

                                <div class="flex justify-end space-x-4">
                                    <button @click="goHome"
                                        class="px-4 py-2 rounded-lg font-medium transition-all duration-300" :class="[
                                            themeStore.isDark
                                                ? 'bg-dark-primary text-dark-text hover:bg-dark-primary/90'
                                                : 'bg-light-primary text-light-text hover:bg-light-primary/90'
                                        ]">
                                        Home
                                    </button>
                                    <button @click="restartGame"
                                        class="px-4 py-2 rounded-lg font-medium transition-all duration-300" :class="[
                                            themeStore.isDark
                                                ? 'bg-dark-accent text-dark-text hover:bg-dark-accent/90'
                                                : 'bg-light-accent text-light-text hover:bg-light-accent/90'
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
import { ref, computed, onMounted, onBeforeUnmount, nextTick } from 'vue'
import { useRouter } from 'vue-router'
import { useThemeStore } from '@/stores/themeStore'
import { Heart } from 'lucide-vue-next'
import {
    TransitionRoot,
    TransitionChild,
    Dialog,
    DialogPanel,
    DialogTitle,
} from '@headlessui/vue'
import AutoResizingText from '@/components/AutoResizingText.vue'
import axios from 'axios'

const router = useRouter()
const themeStore = useThemeStore()

// Состояние игры
const currentLevel = ref(1)
const lives = ref(3)
const score = ref(0)
const gameStartTime = ref(Date.now())
const levelStartTime = ref(Date.now())
const showLevelComplete = ref(false)
const showGameOver = ref(false)

// Игровые данные
const wordsData = ref([])
const currentChunkIndex = ref(0)
const completedPairs = ref({})
const wrongAttempts = ref([])

// Выбранные слова
const selectedEnWord = ref(null)
const selectedRuWord = ref(null)

// Статистика уровня
const levelStats = ref({
    timeSpent: 0,
    accuracy: 100,
    score: 0,
    multipliers: {
        time: 1,
        accuracy: 1,
        level: 1
    }
})

// Вычисляемые свойства
const levelProgress = computed(() => {
    const total = getPairsForLevel(currentLevel.value)
    const completed = Object.keys(completedPairs.value).length
    return (completed / total) * 100
})

const currentEnglishWords = computed(() =>
    wordsData.value.slice(currentChunkIndex.value * 5, (currentChunkIndex.value + 1) * 5)
        .map(word => ({ id: word.id, text: word.text }))
)

const currentRussianWords = computed(() =>
    wordsData.value.slice(currentChunkIndex.value * 5, (currentChunkIndex.value + 1) * 5)
        .map(word => ({ id: word.id, text: word.translation }))
)

const totalWordsMatched = computed(() =>
    Object.keys(completedPairs.value).length
)

const totalTime = computed(() =>
    Math.floor((Date.now() - gameStartTime.value) / 1000)
)

// Методы
function getPairsForLevel(level) {
    const pairsByLevel = {
        1: 10,
        2: 20,
        3: 35,
        4: 45,
        5: 50
    }
    return pairsByLevel[level] || 50
}

async function loadWords() {
    try {
        const response = await axios.post('/api/v1/tasks/generate/word-matching', {
            task_type: 'word_matching',
            params: {
                pairs_count: getPairsForLevel(currentLevel.value),
                difficulty: getDifficultyForLevel(currentLevel.value)
            }
        })

        wordsData.value = response.data.result.content.originals.map((word, index) => ({
            id: word.id,
            text: word.text,
            translation: response.data.result.content.translations[index].text
        }))

        currentChunkIndex.value = 0
        completedPairs.value = {}
        wrongAttempts.value = []
        levelStartTime.value = Date.now()

    } catch (error) {
        console.error('Error loading words:', error)
    }
}

function getDifficultyForLevel(level) {
    const difficulties = {
        1: 'beginner',
        2: 'basic',
        3: 'intermediate',
        4: 'advanced',
        5: 'advanced'
    }
    return difficulties[level] || 'advanced'
}

function selectWord(word, type) {
    if (completedPairs.value[word.id]) return

    if (type === 'en') {
        if (selectedEnWord.value?.id === word.id) {
            selectedEnWord.value = null
        } else {
            selectedEnWord.value = word
            checkPair()
        }
    } else {
        if (selectedRuWord.value?.id === word.id) {
            selectedRuWord.value = null
        } else {
            selectedRuWord.value = word
            checkPair()
        }
    }
}

async function checkPair() {
    if (!selectedEnWord.value || !selectedRuWord.value) return

    const isCorrect = selectedEnWord.value.id === selectedRuWord.value.id

    if (isCorrect) {
        completedPairs.value[selectedEnWord.value.id] = true

        await nextTick()

        // Если текущий чанк завершен
        const chunkComplete = currentEnglishWords.value
            .every(word => completedPairs.value[word.id])

        if (chunkComplete) {
            if (currentChunkIndex.value * 5 + 5 < getPairsForLevel(currentLevel.value)) {
                // Переход к следующему чанку
                setTimeout(() => {
                    currentChunkIndex.value++
                }, 500)
            } else {
                // Уровень завершен
                await validateLevel()
                showLevelComplete.value = true
            }
        }
    } else {
        wrongAttempts.value.push({
            selected: { en: selectedEnWord.value.id, ru: selectedRuWord.value.id },
            timestamp: Date.now()
        })

        // Анимация ошибки
        const elements = document.querySelectorAll(`[data-word-id="${selectedEnWord.value.id}"], [data-word-id="${selectedRuWord.value.id}"]`)
        elements.forEach(el => {
            el.classList.add('shake-animation')
            setTimeout(() => el.classList.remove('shake-animation'), 500)
        })

        lives.value--
        if (lives.value <= 0) {
            showGameOver.value = true
        }
    }

    // Сброс выбранных слов
    selectedEnWord.value = null
    selectedRuWord.value = null
}

async function validateLevel() {
    try {
        const timeSpent = Math.floor((Date.now() - levelStartTime.value) / 1000)
        const response = await axios.post('/api/v1/tasks/generate/word-matching/validate', {
            task_id: 'word_matching_current',
            pairs: completedPairs.value,
            wrong_attempts: wrongAttempts.value,
            time_spent: timeSpent,
            level: currentLevel.value,
            lives: lives.value,
            current_score: score.value
        })

        levelStats.value = {
            timeSpent,
            accuracy: response.data.statistics.accuracy,
            score: response.data.score_data.final_score,
            multipliers: {
                time: response.data.score_data.time_multiplier,
                accuracy: response.data.score_data.accuracy_multiplier,
                level: response.data.score_data.level_multiplier
            }
        }

        score.value += response.data.score_data.final_score

    } catch (error) {
        console.error('Error validating level:', error)
    }
}

function formatTime(seconds) {
    const minutes = Math.floor(seconds / 60)
    const remainingSeconds = seconds % 60
    return `${minutes}:${remainingSeconds.toString().padStart(2, '0')}`
}

function proceedToNextLevel() {
    if (currentLevel.value < 5) {
        currentLevel.value++
        showLevelComplete.value = false
        loadWords()
    } else {
        showGameOver.value = true
    }
}

function restartGame() {
    currentLevel.value = 1
    lives.value = 3
    score.value = 0
    gameStartTime.value = Date.now()
    showGameOver.value = false
    loadWords()
}

function goHome() {
    router.push('/')
}

// Инициализация
onMounted(() => {
    loadWords()
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

@keyframes shake {

    0%,
    100% {
        transform: translateX(0);
    }

    25% {
        transform: translateX(-5px);
    }

    75% {
        transform: translateX(5px);
    }
}

.shake-animation {
    animation: shake 0.5s ease-in-out;
}
</style>