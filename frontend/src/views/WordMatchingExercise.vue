<!-- src/views/WordMatchingExercise.vue -->
<template>
    <div class="container mx-auto px-4 py-8">
        <!-- Заголовок и статистика -->
        <header class="mb-8">
            <div class="flex justify-between items-center mb-4">
                <h1 class="text-2xl font-bold" :class="[themeStore.isDark ? 'text-dark-text' : 'text-light-text']">
                    Word Matching
                </h1>
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
                                    themeStore.isDark ? 'bg-dark-secondary' : 'bg-light-secondary',
                                    selectedEnWord?.id === word.id ? 'ring-4 ring-green-500 animate-pulse' : '',
                                    completedPairs[word.id]
                                        ? [
                                            themeStore.isDark ? 'opacity-50 bg-green-800' : 'opacity-50 bg-green-200',
                                            'cursor-not-allowed',
                                        ]
                                        : 'hover:scale-105',
                                ]">
                                <AutoResizingText :text="word.text" />
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
                                    themeStore.isDark ? 'bg-dark-secondary' : 'bg-light-secondary',
                                    selectedRuWord?.id === word.id ? 'ring-4 ring-green-500 animate-pulse' : '',
                                    completedPairs[word.id]
                                        ? [
                                            themeStore.isDark ? 'opacity-50 bg-green-800' : 'opacity-50 bg-green-200',
                                            'cursor-not-allowed',
                                        ]
                                        : 'hover:scale-105',
                                ]">
                                <AutoResizingText :text="word.text" />
                                <div v-if="completedPairs[word.id]"
                                    class="absolute inset-0 rounded-lg border-4 border-green-500 animate-success"></div>
                            </button>
                        </div>
                    </template>
                </TransitionGroup>
            </div>
        </div>
    </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { useThemeStore } from '@/stores/themeStore'
import { useAuthStore } from '@/stores/authStore'
import AutoResizingText from '@/components/AutoResizingText.vue'
import axios from 'axios'

const router = useRouter()
const themeStore = useThemeStore()
const authStore = useAuthStore()

const currentBatch = ref(0)
const completedPairs = ref({})
const wrongAttempts = ref([])
const selectedEnWord = ref(null)
const selectedRuWord = ref(null)
const currentEnglishWords = ref([])
const currentRussianWords = ref([])
const loading = ref(false)
const batchStartTime = ref(Date.now())

// Разбиваем слова на батчи
const englishWordBatches = computed(() => {
    return chunk(currentEnglishWords.value, 5)
})

const russianWordBatches = computed(() => {
    return chunk(currentRussianWords.value, 5)
})

// Функция для разбивки массива на батчи
function chunk(array, size) {
    const chunks = []
    for (let i = 0; i < array.length; i += size) {
        chunks.push(array.slice(i, i + size))
    }
    return chunks
}

// Перемешивание массива
function shuffleArray(array) {
    for (let i = array.length - 1; i > 0; i--) {
        const j = Math.floor(Math.random() * (i + 1))
            ;[array[i], array[j]] = [array[j], array[i]]
    }
    return array
}

// Загрузка слов
async function loadWords() {
    loading.value = true
    try {
        const params = {
            task_type: "word_matching",
            user_id: authStore.user?.id,
            params: {
                pairs_count: 15
            }
        }

        const response = await axios.post('/api/v1/tasks/generate/word-matching', params)
        const data = response.data.result.content

        // Разбиваем на батчи сразу
        let batches = []
        for (let i = 0; i < data.originals.length; i += 5) {
            const batchOriginals = data.originals.slice(i, i + 5)
            const batchTranslations = data.translations.slice(i, i + 5)
            batches.push({
                originals: batchOriginals,
                translations: shuffleArray([...batchTranslations])
            })
        }

        currentEnglishWords.value = batches.map(batch => batch.originals).flat()
        currentRussianWords.value = batches.map(batch => batch.translations).flat()

        // Сбрасываем состояние
        currentBatch.value = 0
        completedPairs.value = {}
        wrongAttempts.value = []
        batchStartTime.value = Date.now()

        return response.data
    } catch (error) {
        console.error('Error loading words:', error)
        throw error
    } finally {
        loading.value = false
    }
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
async function checkPair() {
    const isCorrect = selectedEnWord.value.id === selectedRuWord.value.id

    if (isCorrect) {
        completedPairs.value[selectedEnWord.value.id] = true

        // Проверяем завершение текущего батча
        const currentBatchWords = englishWordBatches.value[currentBatch.value]
        const allBatchWordsCompleted = currentBatchWords.every(word => completedPairs.value[word.id])

        if (allBatchWordsCompleted) {
            // Отправляем статистику по завершенному батчу
            await sendBatchStatistics()

            // Если осталось меньше 10 слов, загружаем новые
            if (Object.keys(completedPairs.value).length >= englishWordBatches.value.length - 10) {
                await loadWords()
            } else if (currentBatch.value < englishWordBatches.value.length - 1) {
                setTimeout(() => {
                    currentBatch.value++
                }, 1000)
            }
        }
    } else {
        wrongAttempts.value.push({
            word_id: selectedEnWord.value.id,
            wrong_translation_id: selectedRuWord.value.id,
            timestamp: Date.now(),
        })
    }

    // Сбрасываем выбор
    selectedEnWord.value = null
    selectedRuWord.value = null
}

// Отправка статистики по батчу
async function sendBatchStatistics() {
    const currentBatchWords = englishWordBatches.value[currentBatch.value]
    const batchPairs = {}
    const correctPairs = {}

    currentBatchWords.forEach(word => {
        if (completedPairs.value[word.id]) {
            const translation = currentRussianWords.value.find(w => w.id === word.id)
            if (translation) {
                batchPairs[String(word.id)] = translation.text
                correctPairs[String(word.id)] = translation.text
            }
        }
    })

    const batchWrongAttempts = wrongAttempts.value.filter(attempt =>
        currentBatchWords.some(word => word.id === attempt.word_id)
    ).map(attempt => ({
        word_id: Number(attempt.word_id),
        wrong_translation_id: Number(attempt.wrong_translation_id),
        timestamp: attempt.timestamp
    }))

    try {
        const validationData = {
            task_id: `word_matching_batch_${currentBatch.value}`,
            user_pairs: batchPairs,
            correct_pairs: correctPairs,
            wrong_attempts: batchWrongAttempts,
            time_spent: Math.floor((Date.now() - batchStartTime.value) / 1000)
        }

        console.log('Sending batch statistics:', validationData)

        const response = await axios.post(
            '/api/v1/tasks/generate/word-matching/validate',
            {
                headers: {
                    'Content-Type': 'application/json'
                }
            }
        )

        wrongAttempts.value = wrongAttempts.value.filter(attempt =>
            !currentBatchWords.some(word => word.id === attempt.word_id)
        )

        batchStartTime.value = Date.now()
        return response.data
    } catch (error) {
        console.error('Error sending batch statistics:', error)
    }
}

// Инициализация
onMounted(async () => {
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
