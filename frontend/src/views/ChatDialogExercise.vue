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
                                        <div class="p-4 rounded-lg"
                                            :class="[themeStore.isDark ? 'bg-dark-primary/50' : 'bg-light-primary/50']">
                                            <p class="text-base"
                                                :class="[themeStore.isDark ? 'text-dark-text' : 'text-light-text']">
                                                {{ message.text }}
                                            </p>
                                            <button @click="toggleTranslation(index)"
                                                class="mt-2 inline-flex items-center space-x-1 opacity-50 hover:opacity-100 transition-opacity text-xs"
                                                :class="[themeStore.isDark ? 'text-dark-text' : 'text-light-text']">
                                                <Languages class="w-4 h-4" />
                                            </button>
                                            <Transition name="fade">
                                                <p v-if="showTranslations[index]" class="mt-2 text-sm opacity-70"
                                                    :class="[themeStore.isDark ? 'text-dark-text' : 'text-light-text']">
                                                    {{ message.translation }}
                                                </p>
                                            </Transition>
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
                                        <button @click="toggleTranslation(index)"
                                            class="mt-2 inline-flex items-center space-x-1 opacity-50 hover:opacity-100 transition-opacity text-xs"
                                            :class="[themeStore.isDark ? 'text-dark-text' : 'text-light-text']">
                                            <Languages class="w-4 h-4" />
                                        </button>
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

            <!-- Message Processor для текущего сообщения пользователя -->
            <MessageProcessor v-if="currentUserMessage" :message="currentUserMessage" @message-complete="sendMessage"
                :class="[themeStore.isDark ? 'bg-dark-secondary' : 'bg-light-secondary']" />
        </div>
    </div>
</template>

<script setup>
import { ref, onMounted, nextTick } from 'vue'
import { useThemeStore } from '@/stores/themeStore'
import { useAuthStore } from '@/stores/authStore'
import { Loader2Icon, Languages } from 'lucide-vue-next'
import WordTermSelector from '@/components/WordTermSelector.vue'
import MessageProcessor from '@/components/MessageProcessor.vue'
import axios from 'axios'

const themeStore = useThemeStore()
const authStore = useAuthStore()
const chatContainer = ref(null)

const messages = ref([])
const currentUserMessage = ref(null)
const showTranslations = ref({})

const availableWords = ref([])
const availableTerms = ref([])
const selection = ref({ words: [], terms: [] })
const isGenerating = ref(false)
const exercise = ref(null)

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

async function sendMessage(processedMessage) {
    // Добавляем сообщение с анимацией
    messages.value.push(processedMessage)

    // Прокручиваем к новому сообщению
    await scrollToBottom()

    // Сбрасываем текущее сообщение
    currentUserMessage.value = null

    // Пауза перед следующим сообщением
    await new Promise(resolve => setTimeout(resolve, 1000))

    // Находим и показываем следующее сообщение
    const currentIndex = messages.value.length
    if (exercise.value?.content.messages[currentIndex]) {
        await showNextMessage(currentIndex)
    }
}

async function showNextMessage(index) {
    if (!exercise.value?.content.messages[index]) return;

    const message = { ...exercise.value.content.messages[index] }

    if (!message.is_user_message) {
        // Показываем сообщение бота с небольшой задержкой, имитируя набор текста
        await new Promise(resolve => setTimeout(resolve, 500))
        messages.value.push(message)
        await scrollToBottom()

        // Добавляем задержку перед следующим сообщением
        await new Promise(resolve => setTimeout(resolve, 1500))

        if (index + 1 < exercise.value.content.messages.length) {
            const nextMessage = exercise.value.content.messages[index + 1]
            if (nextMessage.is_user_message) {
                // Если следующее сообщение от пользователя, устанавливаем его как текущее
                currentUserMessage.value = nextMessage
            } else {
                await showNextMessage(index + 1)
            }
        }
    } else {
        // Устанавливаем сообщение пользователя как текущее с небольшой задержкой
        await new Promise(resolve => setTimeout(resolve, 500))
        currentUserMessage.value = message
    }
}

function toggleTranslation(index) {
    showTranslations.value[index] = !showTranslations.value[index]
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
    showTranslations.value = {}
    currentUserMessage.value = null

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

onMounted(async () => {
    await loadAvailableItems()
})
</script>

<style scoped>
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
</style>