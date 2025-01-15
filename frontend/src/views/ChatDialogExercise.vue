// src/views/ChatDialogExercise.vue
<template>
    <div class="container mx-auto px-4 py-8">
        <!-- Header section -->
        <header class="text-center mb-8">
            <h1 class="text-2xl font-bold mb-2" :class="[themeStore.isDark ? 'text-dark-text' : 'text-light-text']">
                Чат-диалог
            </h1>
            <p class="text-sm" :class="[themeStore.isDark ? 'text-dark-text/70' : 'text-light-text/70']">
                Заполните пропуски в диалоге, выбрав правильные слова
            </p>
        </header>

        <!-- Parameters section -->
        <Transition name="fade">
            <div v-if="!exercise" class="max-w-2xl mx-auto mb-8">
                <div class="p-6 rounded-lg shadow-lg"
                    :class="[themeStore.isDark ? 'bg-dark-secondary' : 'bg-light-secondary']">
                    <WordTermSelector :words="availableWords" :terms="availableTerms"
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

        <!-- Chat and input section -->
        <div v-if="exercise" class="max-w-2xl mx-auto flex flex-col h-[600px]">
            <!-- Chat messages -->
            <div class="flex-1 p-6 rounded-t-lg shadow-lg overflow-y-auto"
                :class="[themeStore.isDark ? 'bg-dark-secondary' : 'bg-light-secondary']" ref="chatContainer">
                <TransitionGroup name="chat-message" tag="div" class="space-y-6">
                    <div v-for="(message, index) in messages" :key="index"
                        :class="[message.is_user_message ? 'flex justify-end' : '']">
                        <div class="max-w-[80%]">
                            <!-- Bot message -->
                            <template v-if="!message.is_user_message">
                                <div class="flex items-start space-x-4">
                                    <div class="space-y-2">
                                        <div class="text-sm font-medium"
                                            :class="[themeStore.isDark ? 'text-dark-text' : 'text-light-text']">
                                            {{ message.author }}
                                        </div>

                                        <!-- Typing animation -->
                                        <div v-if="message.isTyping" class="flex items-center space-x-1">
                                            <span class="text-sm opacity-70">печатает</span>
                                            <span class="flex space-x-1">
                                                <span class="animate-bounce">.</span>
                                                <span class="animate-bounce" style="animation-delay: 0.2s">.</span>
                                                <span class="animate-bounce" style="animation-delay: 0.4s">.</span>
                                            </span>
                                        </div>

                                        <div v-else class="p-4 rounded-lg"
                                            :class="[themeStore.isDark ? 'bg-dark-primary/50' : 'bg-light-primary/50']">
                                            <p class="text-base"
                                                :class="[themeStore.isDark ? 'text-dark-text' : 'text-light-text']">
                                                {{ message.text }}
                                            </p>
                                        </div>
                                    </div>
                                </div>
                            </template>

                            <!-- User message -->
                            <template v-else>
                                <div class="space-y-2">
                                    <div class="text-sm font-medium text-right"
                                        :class="[themeStore.isDark ? 'text-dark-text' : 'text-light-text']">
                                        Вы
                                    </div>
                                    <div class="p-4 rounded-lg"
                                        :class="[themeStore.isDark ? 'bg-dark-primary/50' : 'bg-light-primary/50']">
                                        <p class="text-base"
                                            :class="[themeStore.isDark ? 'text-dark-text' : 'text-light-text']">
                                            {{ message.text }}
                                        </p>

                                        <!-- Translation toggle -->
                                        <button @click="toggleTranslation(index)"
                                            class="mt-2 inline-flex items-center space-x-1 opacity-50 hover:opacity-100 transition-opacity text-xs"
                                            :class="[themeStore.isDark ? 'text-dark-text' : 'text-light-text']">
                                            <Languages class="w-4 h-4" />
                                        </button>

                                        <!-- Translation text -->
                                        <Transition name="fade">
                                            <p v-if="showTranslations[index]" class="mt-2 text-sm opacity-70"
                                                :class="[themeStore.isDark ? 'text-dark-text' : 'text-light-text']">
                                                {{ message.translation }}
                                            </p>
                                        </Transition>
                                    </div>
                                </div>
                            </template>
                        </div>
                    </div>
                </TransitionGroup>
            </div>

            <!-- Input section -->
            <div class="border-t" :class="[themeStore.isDark ? 'bg-dark-secondary' : 'bg-light-secondary']">
                <div class="p-4 relative">
                    <!-- Input field -->
                    <div class="min-h-[40px] p-3 rounded-lg bg-opacity-50 relative"
                        :class="[themeStore.isDark ? 'bg-dark-primary' : 'bg-light-primary']">
                        <div v-if="currentUserMessage" class="pr-20">
                            <!-- Text before gap -->
                            <TypeWriter :text="getMessagePartBeforeGap(currentUserMessage)" :typing-speed="50"
                                @complete="onInputTypingComplete" />

                            <!-- Current gap -->
                            <span v-if="currentGapIndex !== null" :class="[
                                'px-2 py-1 rounded mx-1 transition-all duration-300',
                                getGapHighlightClass(currentUserMessage.gaps[currentGapIndex].id)
                            ]">
                                {{ selectedAnswers[currentUserMessage.gaps[currentGapIndex].id] || '...' }}
                            </span>

                            <!-- Text between gaps -->
                            <TypeWriter v-if="shouldShowNextPart"
                                :text="getMessagePartBetweenGaps(currentUserMessage, currentGapIndex)"
                                :typing-speed="50" @complete="onMiddlePartTypingComplete" />
                        </div>

                        <!-- Translation toggle for input -->
                        <button v-if="currentUserMessage && !isMessageComplete" @click="toggleInputTranslation"
                            class="absolute right-2 top-1/2 transform -translate-y-1/2 px-2 py-1 rounded opacity-50 hover:opacity-100 transition-opacity"
                            :class="[themeStore.isDark ? 'text-dark-text' : 'text-light-text']">
                            <Languages class="w-4 h-4" />
                        </button>

                        <!-- Send button -->
                        <button v-if="isMessageComplete" @click="sendMessage"
                            class="absolute right-2 top-1/2 transform -translate-y-1/2 px-4 py-2 rounded-lg transition-all duration-300"
                            :class="[themeStore.isDark ? 'bg-dark-accent hover:bg-dark-accent/90' : 'bg-light-accent hover:bg-light-accent/90']">
                            Отправить
                        </button>
                    </div>

                    <!-- Translation for current input -->
                    <Transition name="fade">
                        <p v-if="showInputTranslation && currentUserMessage" class="mt-2 text-sm opacity-70 px-3"
                            :class="[themeStore.isDark ? 'text-dark-text' : 'text-light-text']">
                            {{ getMessagePartBeforeGap(currentUserMessage, true) }}
                        </p>
                    </Transition>
                </div>

                <!-- Options keyboard -->
                <Transition name="option-list">
                    <div v-if="currentGapIndex !== null && !isMessageComplete" class="p-4 border-t">
                        <div class="grid grid-cols-2 gap-4">
                            <TransitionGroup name="option">
                                <button v-for="option in currentUserMessage?.gaps[currentGapIndex]?.options"
                                    :key="option.word"
                                    @click="selectAnswer(currentUserMessage.gaps[currentGapIndex].id, option.word)"
                                    :disabled="isOptionDisabled(currentUserMessage.gaps[currentGapIndex].id, option.word)"
                                    :class="[
                                        'p-4 rounded-lg text-left transition-all duration-300',
                                        getOptionClass(currentUserMessage.gaps[currentGapIndex].id, option.word)
                                    ]">
                                    <div class="space-y-1">
                                        <span class="block font-medium">{{ option.word }}</span>
                                        <span class="block text-sm opacity-70">{{ option.translation }}</span>
                                    </div>
                                </button>
                            </TransitionGroup>
                        </div>
                    </div>
                </Transition>
            </div>
        </div>
    </div>
</template>

<script setup>
import { ref, computed, onMounted, defineComponent, h, nextTick, watch, onBeforeUnmount } from 'vue'
import { useThemeStore } from '@/stores/themeStore'
import { useAuthStore } from '@/stores/authStore'
import { Loader2Icon, Languages } from 'lucide-vue-next'
import WordTermSelector from '@/components/WordTermSelector.vue'
import axios from 'axios'

// States
const themeStore = useThemeStore()
const authStore = useAuthStore()
const chatContainer = ref(null)
const showInputTranslation = ref(false)

const availableWords = ref([])
const availableTerms = ref([])
const selection = ref({ words: [], terms: [] })
const isGenerating = ref(false)
const exercise = ref(null)
const messages = ref([])
const showTranslations = ref({})
const selectedAnswers = ref({})
const wrongAttempts = ref({})

const currentUserMessage = ref(null)
const currentGapIndex = ref(null)
const isMessageComplete = ref(false)
const shouldShowNextPart = ref(false)
const attemptsCount = ref({})

// TypeWriter component
const TypeWriter = defineComponent({
    props: {
        text: { type: String, required: true },
        typingSpeed: { type: Number, default: 50 }
    },
    emits: ['complete'],
    setup(props, { emit }) {
        const displayedText = ref('')
        let timeoutId = null

        function typeText(text) {
            let currentIndex = 0
            displayedText.value = ''

            function typeNextCharacter() {
                if (currentIndex < text.length) {
                    displayedText.value += text[currentIndex]
                    currentIndex++
                    timeoutId = setTimeout(typeNextCharacter, props.typingSpeed)
                } else {
                    emit('complete')
                }
            }

            typeNextCharacter()
        }

        watch(() => props.text, (newText) => {
            if (timeoutId) {
                clearTimeout(timeoutId)
            }
            typeText(newText)
        }, { immediate: true })

        onBeforeUnmount(() => {
            if (timeoutId) {
                clearTimeout(timeoutId)
                timeoutId = null
            }
        })

        return () => h('span', displayedText.value)
    }
})

// Methods
function getMessagePartBeforeGap(message, isTranslation = false) {
    if (!message.gaps || !message.gaps.length) return isTranslation ? message.translation : message.text

    const text = isTranslation ? message.translation : message.text
    const firstGap = message.gaps[0]
    const parts = text.split(`{gap${firstGap.id}}`)

    return parts[0]
}

function getMessagePartBetweenGaps(message, currentIndex) {
    if (!message.gaps || !message.gaps.length) return ''

    const currentGap = message.gaps[currentIndex]
    const parts = message.text.split(`{gap${currentGap.id}}`)

    if (currentIndex >= message.gaps.length - 1) {
        return parts[1] || ''
    }

    const nextGap = message.gaps[currentIndex + 1]
    const textAfterCurrentGap = parts[1] || ''
    const nextParts = textAfterCurrentGap.split(`{gap${nextGap.id}}`)
    return nextParts[0] || ''
}

function toggleInputTranslation() {
    showInputTranslation.value = !showInputTranslation.value
}

async function selectAnswer(gapId, answer) {
    if (isOptionDisabled(gapId, answer)) return

    const gap = currentUserMessage.value.gaps[currentGapIndex.value]
    const isCorrect = gap.correct === answer

    if (isCorrect) {
        selectedAnswers.value[gapId] = answer
        await new Promise(resolve => setTimeout(resolve, 500))

        if (currentGapIndex.value < currentUserMessage.value.gaps.length - 1) {
            currentGapIndex.value++
            shouldShowNextPart.value = true
        } else {
            isMessageComplete.value = true
        }
    } else {
        wrongAttempts.value[gapId] = answer
        attemptsCount.value[gapId] = (attemptsCount.value[gapId] || 0) + 1

        if (attemptsCount.value[gapId] >= 2) {
            selectedAnswers.value
            selectedAnswers.value[gapId] = gap.correct
            await new Promise(resolve => setTimeout(resolve, 500))

            if (currentGapIndex.value < currentUserMessage.value.gaps.length - 1) {
                currentGapIndex.value++
                shouldShowNextPart.value = true
            } else {
                isMessageComplete.value = true
            }
        }
    }
}

async function sendMessage() {
    if (!isMessageComplete.value) return

    // Собираем финальный текст сообщения
    let finalText = currentUserMessage.value.text
    for (const gap of currentUserMessage.value.gaps) {
        finalText = finalText.replace(
            `{gap${gap.id}}`,
            selectedAnswers.value[gap.id]
        )
    }

    let finalTranslation = currentUserMessage.value.translation
    for (const gap of currentUserMessage.value.gaps) {
        finalTranslation = finalTranslation.replace(
            `{gap${gap.id}}`,
            currentUserMessage.value.gaps.find(g => g.id === gap.id).options.find(
                o => o.word === selectedAnswers.value[gap.id]
            ).translation
        )
    }

    // Добавляем сообщение в чат
    messages.value.push({
        ...currentUserMessage.value,
        text: finalText,
        translation: finalTranslation
    })

    // Показываем "печатает" для следующего сообщения
    const nextMessageIndex = exercise.value.content.messages.indexOf(currentUserMessage.value) + 1
    if (exercise.value.content.messages[nextMessageIndex]) {
        await showNextMessage(nextMessageIndex)
    }

    // Сбрасываем состояния
    currentUserMessage.value = null
    currentGapIndex.value = null
    isMessageComplete.value = false
    shouldShowNextPart.value = false
    showInputTranslation.value = false
}

async function showNextMessage(index) {
    if (!exercise.value?.content.messages[index]) return

    const message = { ...exercise.value.content.messages[index] }

    if (!message.is_user_message) {
        // Показываем анимацию печати
        const typingMessage = { ...message, isTyping: true }
        messages.value = [...messages.value, typingMessage]
        scrollToBottom()

        // Ждем 1-2 секунды (рандомно)
        const delay = Math.floor(Math.random() * 1000) + 1000
        await new Promise(resolve => setTimeout(resolve, delay))

        // Обновляем сообщение, убирая анимацию печати
        messages.value = [
            ...messages.value.slice(0, -1),
            { ...message, isTyping: false }
        ]

        // Добавляем задержку перед следующим сообщением
        await new Promise(resolve => setTimeout(resolve, 1000))
        await showNextMessage(index + 1)
    } else {
        // Сбрасываем состояния для нового сообщения пользователя
        currentUserMessage.value = message
        currentGapIndex.value = 0
        isMessageComplete.value = false
        shouldShowNextPart.value = false
        attemptsCount.value = {}
        showInputTranslation.value = false
    }

    scrollToBottom()
}

function getOptionClass(gapId, word) {
    const baseClass = themeStore.isDark ? 'bg-dark-primary' : 'bg-light-primary'

    if (selectedAnswers.value[gapId] === word) {
        return `${baseClass} ring-2 ring-green-500 highlight-success`
    }
    if (wrongAttempts.value[gapId] === word) {
        return `${baseClass} ring-2 ring-red-500 opacity-50 highlight-error`
    }
    return `${baseClass} hover:bg-opacity-80`
}

function getGapHighlightClass(gapId) {
    if (selectedAnswers.value[gapId]) {
        return 'bg-green-500/20 border border-green-500'
    }
    if (wrongAttempts.value[gapId]) {
        return 'bg-red-500/20 border border-red-500'
    }
    return 'bg-gray-500/20 border border-gray-500'
}

function isOptionDisabled(gapId, word) {
    return wrongAttempts.value[gapId] === word || selectedAnswers.value[gapId]
}

function updateSelection(newSelection) {
    selection.value = newSelection
}

function scrollToBottom() {
    nextTick(() => {
        if (chatContainer.value) {
            chatContainer.value.scrollTop = chatContainer.value.scrollHeight
        }
    })
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
    messages.value = []
    selectedAnswers.value = {}
    wrongAttempts.value = {}
    showTranslations.value = {}
    currentUserMessage.value = null
    currentGapIndex.value = null
    isMessageComplete.value = false
    shouldShowNextPart.value = false
    attemptsCount.value = {}
    showInputTranslation.value = false

    try {
        const request = {
            task_type: 'chat_dialog',
            user_id: authStore.user?.id,
            params: {
                messages_count: 5,
                words: selection.value.words,
                terms: selection.value.terms,
                difficulty: 'intermediate'
            }
        }

        const response = await axios.post('/api/v1/tasks/generate/chat-dialog', request)
        exercise.value = response.data.result
        await showNextMessage(0)
    } catch (error) {
        console.error('Error generating exercise:', error)
    } finally {
        isGenerating.value = false
    }
}

async function checkAnswers() {
    try {
        const correctAnswers = messages.value
            .filter(msg => msg.is_user_message)
            .flatMap(msg => msg.gaps.map(gap => ({ [gap.id]: gap.correct })))
            .reduce((acc, val) => ({ ...acc, ...val }), {})

        const response = await axios.post('/api/v1/tasks/generate/chat-dialog/validate', {
            task_id: exercise.value.task_id,
            user_answers: selectedAnswers.value,
            correct_answers: correctAnswers,
            used_items: exercise.value.metadata?.used_terms || [],
            item_types: exercise.value.metadata?.used_terms?.reduce((acc, term) => ({ ...acc, [term]: 'term' }), {}) || {},
            user_id: authStore.user?.id,
        })

        if (response.data.is_successful) {
            setTimeout(() => {
                exercise.value = null
                generateExercise()
            }, 1500)
        }
    } catch (error) {
        console.error('Error checking answers:', error)
    }
}

function toggleTranslation(index) {
    showTranslations.value[index] = !showTranslations.value[index]
}

function onInputTypingComplete() {
    if (currentUserMessage.value?.gaps[currentGapIndex.value]) {
        shouldShowNextPart.value = false
    }
}

function onMiddlePartTypingComplete() {
    if (currentUserMessage.value?.gaps[currentGapIndex.value]) {
        shouldShowNextPart.value = false
    }
}

onMounted(async () => {
    await loadAvailableItems()
})
</script>

<style scoped>
/* Анимации для подсветки ответов */
@keyframes highlight-success {

    0%,
    100% {
        transform: scale(1);
    }

    50% {
        transform: scale(1.05);
    }
}

@keyframes highlight-error {
    0% {
        box-shadow: 0 0 0 0 rgba(239, 68, 68, 0.4);
    }

    70% {
        box-shadow: 0 0 0 10px rgba(239, 68, 68, 0);
    }

    100% {
        box-shadow: 0 0 0 0 rgba(239, 68, 68, 0);
    }
}

.highlight-success {
    animation: highlight-success 1s cubic-bezier(0.4, 0, 0.2, 1);
}

.highlight-error {
    animation: highlight-error 0.5s ease-in-out;
}

.chat-message-enter-active,
.chat-message-leave-active {
    transition: all 0.3s ease;
}

.chat-message-enter-from {
    opacity: 0;
    transform: translateY(20px);
}

.chat-message-leave-to {
    opacity: 0;
    transform: translateY(-20px);
}

.fade-enter-active,
.fade-leave-active {
    transition: opacity 0.3s ease;
}

.fade-enter-from,
.fade-leave-to {
    opacity: 0;
}

@keyframes bounce {

    0%,
    100% {
        transform: translateY(0);
    }

    50% {
        transform: translateY(-3px);
    }
}

.animate-bounce {
    animation: bounce 0.6s infinite;
}

.option-enter-active,
.option-leave-active {
    transition: all 0.3s ease-out;
}

.option-enter-from {
    opacity: 0;
    transform: translateY(20px);
}

.option-leave-to {
    opacity: 0;
    transform: translateY(-20px);
}

.option-list-enter-active,
.option-list-leave-active {
    transition: all 0.3s ease-out;
}

.option-list-enter-from {
    opacity: 0;
    transform: translateY(-20px);
}

.option-list-leave-to {
    opacity: 0;
    transform: translateY(20px);
}
</style>