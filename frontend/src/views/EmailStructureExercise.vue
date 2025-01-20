// src/views/EmailStructureExercise.vue
<template>
    <div class="container mx-auto px-4 py-2">
        <!-- Заголовок -->
        <header class="text-center mb-4">
            <h1 class="text-2xl font-bold mb-2" :class="[themeStore.isDark ? 'text-dark-text' : 'text-light-text']">
                Структура Email
            </h1>
            <p v-if="exercise" class="text-sm"
                :class="[themeStore.isDark ? 'text-dark-text/70' : 'text-light-text/70']">
                {{ exercise.content.context }}
            </p>
        </header>

        <div class="max-w-4xl mx-auto">
            <!-- Селектор слов и терминов -->
            <Transition name="fade">
                <div v-if="!exercise" class="mb-8">
                    <div class="p-6 rounded-lg shadow-lg"
                        :class="[themeStore.isDark ? 'bg-dark-secondary' : 'bg-light-secondary']">
                        <WordTermSelector :words="availableWords" :terms="availableTerms" :max-words="3" :max-terms="2"
                            @update:selection="updateSelection" />

                        <button @click="generateExercise" :disabled="isGenerating"
                            class="w-full mt-4 py-3 rounded-lg font-medium transition-all duration-300 flex items-center justify-center space-x-2"
                            :class="[
                                themeStore.isDark
                                    ? 'bg-dark-accent text-dark-text hover:bg-dark-accent/90'
                                    : 'bg-light-accent text-light-text hover:bg-light-accent/90',
                                isGenerating ? 'opacity-75 cursor-not-allowed' : ''
                            ]">
                            <span v-if="isGenerating" class="animate-spin">
                                <Loader2Icon class="w-5 h-5" />
                            </span>
                            <span>{{ isGenerating ? 'Генерация...' : 'Сгенерировать задание' }}</span>
                        </button>
                    </div>
                </div>
            </Transition>

            <!-- Основное содержимое -->
            <Transition name="fade">
                <div v-if="exercise" class="flex flex-col md:flex-row gap-6">
                    <!-- Email структура -->
                    <div class="w-full md:w-2/3 mx-auto">
                        <div class="space-y-4 p-6 rounded-lg shadow-lg overflow-y-auto max-h-[calc(100vh-12rem)]"
                            :class="[themeStore.isDark ? 'bg-dark-secondary' : 'bg-light-secondary']">
                            <TransitionGroup name="list" tag="div" class="space-y-4">
                                <div v-for="block in emailBlocks" :key="block.id" class="relative">
                                    <!-- Блок с содержимым или пустой блок для выбора -->
                                    <div v-if="!block.isEmpty" class="p-4 rounded-lg transition-all"
                                        :class="[getBlockClass(block)]">
                                        <p class="mb-2">{{ block.content }}</p>
                                        <button @click="toggleTranslation(block.id)"
                                            class="text-xs opacity-50 hover:opacity-100 transition-opacity inline-flex items-center space-x-1">
                                            <Languages class="w-4 h-4" />
                                            <span>{{ showTranslations[block.id] ? 'Скрыть перевод' : 'Показать перевод'
                                                }}</span>
                                        </button>
                                        <Transition name="fade">
                                            <p v-if="showTranslations[block.id]" class="mt-2 text-sm opacity-70">
                                                {{ block.translation }}
                                            </p>
                                        </Transition>
                                    </div>
                                    <div v-else @click="selectBlock(block)"
                                        class="p-4 rounded-lg border-2 border-dashed cursor-pointer transition-all hover:border-solid min-h-[100px] flex items-center justify-center"
                                        :class="[
                                            themeStore.isDark
                                                ? 'border-dark-accent/50 hover:border-dark-accent'
                                                : 'border-light-accent/50 hover:border-light-accent'
                                        ]">
                                        <span class="opacity-50">Нажмите, чтобы выбрать контент</span>
                                    </div>

                                    <!-- Иконка ошибки и подсказка -->
                                    <div v-if="showResults && !block.isCorrect && !block.isEmpty"
                                        class="absolute -right-2 -top-2">
                                        <button @click="toggleHint(block.id)"
                                            class="w-6 h-6 rounded-full flex items-center justify-center" :class="[
                                                themeStore.isDark
                                                    ? 'bg-dark-accent text-dark-text'
                                                    : 'bg-light-accent text-light-text'
                                            ]">
                                            <HelpCircle class="w-4 h-4" />
                                        </button>
                                        <Transition name="fade">
                                            <div v-if="showHints[block.id]"
                                                class="absolute right-0 mt-2 w-64 p-4 rounded-lg shadow-lg z-10" :class="[
                                                    themeStore.isDark
                                                        ? 'bg-dark-primary text-dark-text'
                                                        : 'bg-light-primary text-light-text'
                                                ]">
                                                {{ block.whyWrong }}
                                            </div>
                                        </Transition>
                                    </div>
                                </div>
                            </TransitionGroup>

                            <!-- Кнопка проверки -->
                            <div v-if="isComplete && !showResults" class="sticky bottom-0 pt-4 mt-6 bg-inherit">
                                <button @click="checkAnswer"
                                    class="w-full py-3 rounded-lg font-medium transition-all duration-300" :class="[
                                        themeStore.isDark
                                            ? 'bg-dark-accent text-dark-text hover:bg-dark-accent/90'
                                            : 'bg-light-accent text-light-text hover:bg-light-accent/90'
                                    ]">
                                    Проверить
                                </button>
                            </div>
                        </div>
                    </div>

                    <!-- Панель выбора блока (справа на десктопе) -->
                    <Transition name="slide">
                        <div v-if="selectedEmptyBlock" class="w-full md:w-1/3">
                            <div class="sticky top-4 space-y-4 p-6 rounded-lg shadow-lg"
                                :class="[themeStore.isDark ? 'bg-dark-secondary' : 'bg-light-secondary']">
                                <h3 class="font-medium mb-4">Выберите вариант:</h3>
                                <div class="space-y-4 md:space-y-4">
                                    <button v-for="option in blockOptions" :key="option.id"
                                        @click="selectOption(option)"
                                        class="w-full p-4 rounded-lg text-left transition-all duration-300 hover:scale-[1.02]"
                                        :class="[
                                            themeStore.isDark
                                                ? 'bg-dark-primary hover:bg-dark-primary/80'
                                                : 'bg-light-primary hover:bg-light-primary/80'
                                        ]">
                                        <p class="mb-2">{{ option.content }}</p>
                                        <p class="text-sm opacity-70">{{ option.translation }}</p>
                                    </button>
                                </div>
                            </div>
                        </div>
                    </Transition>
                </div>
            </Transition>
        </div>
    </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { useThemeStore } from '@/stores/themeStore'
import { useAuthStore } from '@/stores/authStore'
import { Loader2Icon, Languages, HelpCircle } from 'lucide-vue-next'
import WordTermSelector from '@/components/WordTermSelector.vue'
import axios from 'axios'

const themeStore = useThemeStore()
const authStore = useAuthStore()

// Состояния
const exercise = ref(null)
const task_id = ref(null)
const availableWords = ref([])
const availableTerms = ref([])
const selection = ref({ words: [], terms: [] })
const isGenerating = ref(false)
const selectedEmptyBlock = ref(null)
const blockOptions = ref([])
const showTranslations = ref({})
const showHints = ref({})
const showResults = ref(false)
const userSelections = ref({})

// Email blocks с добавленными пустыми блоками
const emailBlocks = computed(() => {
    if (!exercise.value) return []

    const blocks = []
    const correctBlocks = exercise.value.content.correct_blocks
    const incorrectBlocks = exercise.value.content.incorrect_blocks

    correctBlocks.forEach(block => {
        const incorrectBlock = incorrectBlocks.find(ib => ib.type === block.type)
        if (incorrectBlock) {
            // Если есть некорректный блок этого типа, добавляем пустой блок
            blocks.push({
                ...block,
                isEmpty: !userSelections.value[block.type],
                content: userSelections.value[block.type]?.content || '',
                translation: userSelections.value[block.type]?.translation || '',
                isCorrect: userSelections.value[block.type]?.isCorrect
            })
        } else {
            // Если нет некорректного блока, добавляем корректный
            blocks.push({ ...block, isEmpty: false, isCorrect: true })
        }
    })

    return blocks
})

// Проверка завершенности
const isComplete = computed(() => {
    return emailBlocks.value.every(block => !block.isEmpty)
})

function updateSelection(newSelection) {
    selection.value = newSelection
}

async function loadAvailableItems() {
    try {
        const [wordsResponse, termsResponse] = await Promise.all([
            axios.get('/api/v1/words/all'),
            axios.get('/api/v1/terms/all')
        ])
        availableWords.value = wordsResponse.data
        availableTerms.value = termsResponse.data
    } catch (error) {
        console.error('Error loading items:', error)
    }
}

async function generateExercise() {
    if (isGenerating.value) return

    isGenerating.value = true
    showResults.value = false
    userSelections.value = {}

    try {
        const request = {
            task_type: 'email_structure',
            user_id: authStore.user?.id,
            params: {
                terms: selection.value.terms.map(term => term),
                words: selection.value.words.map(term => term),
                difficulty: 'intermediate'
            }
        }

        console.log('Generating exercise with request:', request)

        const response = await axios.post('/api/v1/tasks/generate/email-structure', request)
        exercise.value = response.data.result
        task_id.value = response.data.task_id
        console.log('Generated exercise:', exercise.value)
        console.log('Task ID:', task_id.value)
    } catch (error) {
        console.error('Error generating exercise:', error)
    } finally {
        isGenerating.value = false
    }
}

function selectBlock(block) {
    selectedEmptyBlock.value = block
    // Получаем правильный и неправильный варианты для этого типа
    const correctBlock = exercise.value.content.correct_blocks.find(b => b.type === block.type)
    const incorrectBlock = exercise.value.content.incorrect_blocks.find(b => b.type === block.type)

    // Перемешиваем варианты
    blockOptions.value = [correctBlock, incorrectBlock]
        .map(block => ({ ...block, isCorrect: block === correctBlock }))
        .sort(() => Math.random() - 0.5)
}

function selectOption(option) {
    if (!selectedEmptyBlock.value) return

    userSelections.value[selectedEmptyBlock.value.type] = {
        ...option,
        isCorrect: option.isCorrect
    }
    selectedEmptyBlock.value = null
}

function toggleTranslation(blockId) {
    showTranslations.value[blockId] = !showTranslations.value[blockId]
}

function toggleHint(blockId) {
    showHints.value[blockId] = !showHints.value[blockId]
}

function getBlockClass(block) {
    if (showResults.value) {
        return [
            themeStore.isDark ? 'bg-dark-primary' : 'bg-light-primary',
            block.isCorrect
                ? 'ring-2 ring-green-500'
                : 'ring-2 ring-red-500'
        ]
    }
    return themeStore.isDark ? 'bg-dark-primary' : 'bg-light-primary'
}

async function checkAnswer() {
    try {
        const userId = authStore.user?.id;
        if (!userId) {
            console.error('User ID is not available');
            return;
        }

        console.log('Words:', exercise.value.metadata.used_words)
        console.log('Terms:', exercise.value.metadata.udes_terms)

        console.log('Sending request with:', {
            words: exercise.value.metadata.used_words || [],
            terms: exercise.value.metadata.used_terms || []
        });

        const response = await axios.post('/api/v1/tasks/generate/email-structure/validate', {
            task_id: task_id.value,
            user_blocks: emailBlocks.value.map(block => ({
                type: block.type,
                content: block.content,
                translation: block.translation
            })),
            correct_blocks: exercise.value.content.correct_blocks,
            words: exercise.value.metadata.used_words || [],
            terms: exercise.value.metadata.used_terms || []
        });

        showResults.value = true;
        emailBlocks.value.forEach(block => {
            const correctBlock = exercise.value.content.correct_blocks.find(
                b => b.type === block.type
            );
            block.isCorrect = block.content === correctBlock.content;
        });

    } catch (error) {
        console.error('Error validating answer:', error);
        if (error.response) {
            console.error('Error response data:', error.response.data);
        }
    }
}

onMounted(async () => {
    await loadAvailableItems()
})
</script>

<style scoped>
.fade-enter-active,
.fade-leave-active {
    transition: opacity 0.3s ease;
}

.fade-enter-from,
.fade-leave-to {
    opacity: 0;
}

.list-enter-active,
.list-leave-active {
    transition: all 0.3s ease;
}

.list-enter-from,
.list-leave-to {
    opacity: 0;
    transform: translateX(30px);
}

.slide-enter-active,
.slide-leave-active {
    transition: all 0.3s ease;
}

.slide-enter-from,
.slide-leave-to {
    opacity: 0;
    transform: translateX(30px);
}

@media (max-width: 768px) {

    .slide-enter-from,
    .slide-leave-to {
        transform: translateY(30px);
    }
}
</style>