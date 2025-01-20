# src/components/MessageProcessor.vue
<template>
    <div class="p-4 border-t">
        <!-- Текст сообщения -->
        <div class="min-h-[40px] p-3 rounded-lg bg-opacity-50 relative">
            <div class="space-y-2">
                <div class="text-sm font-medium text-right"
                    :class="[themeStore.isDark ? 'text-dark-text' : 'text-light-text']">
                    Вы
                </div>
                <div class="p-4 rounded-lg" :class="[themeStore.isDark ? 'bg-dark-primary/50' : 'bg-light-primary/50']">
                    <p class="text-base" :class="[themeStore.isDark ? 'text-dark-text' : 'text-light-text']">
                        <!-- Текст до gap -->
                        <TypeWriter :text="textBeforeGap" :typing-speed="20" :enabled="!isTypingLocked" новый проп
                            @complete="onTypingComplete" />

                        <!-- Текущий gap -->
                        <span v-if="currentGapIndex !== null" :class="[
                            'px-2 py-1 rounded mx-1 inline',
                            getGapHighlightClass(currentGap?.id)
                        ]">
                            {{ selectedAnswers[currentGap?.id] || '...' }}
                        </span>

                        <!-- Текст после gap -->
                        <TypeWriter v-if="shouldShowNextPart" :text="textAfterGap" :typing-speed="20"
                            @complete="onAfterGapComplete" />
                    </p>

                    <!-- Кнопка отправки -->
                    <button v-if="isComplete" @click="$emit('message-complete', processedMessage)"
                        class="mt-4 px-4 py-2 rounded-lg bg-blue-500 text-white">
                        Отправить
                    </button>
                </div>
            </div>
        </div>

        <!-- Варианты ответов -->
        <div v-if="currentGapIndex !== null && !isComplete" class="mt-4 border-t">
            <div class="grid grid-cols-2 gap-4 p-4">
                <button v-for="option in currentGap?.options" :key="option.word" @click="selectAnswer(option.word)"
                    :disabled="isOptionDisabled(currentGap?.id, option.word)"
                    class="p-4 rounded-lg text-left transition-all duration-300"
                    :class="getOptionClass(currentGap?.id, option.word)">
                    <div class="space-y-1">
                        <span class="block font-medium">{{ option.word }}</span>
                        <span class="block text-sm opacity-70">{{ option.translation }}</span>
                    </div>
                </button>
            </div>
        </div>
    </div>
</template>

<script setup>
import { ref, computed, defineComponent, h, watch, onBeforeUnmount } from 'vue'
import { useThemeStore } from '@/stores/themeStore'

const themeStore = useThemeStore()
const isTypingLocked = ref(false)

// TypeWriter component
const TypeWriter = defineComponent({
    props: {
        text: { type: String, required: true },
        typingSpeed: { type: Number, default: 50 },
        enabled: { type: Boolean, default: true }
    },
    emits: ['complete'],
    setup(props, { emit }) {
        const displayedText = ref('')
        const isTyping = ref(false)
        let timeoutId = null

        function typeText(text, startIndex = 0) {
            if (!text || startIndex >= text.length || !props.enabled) {
                emit('complete')
                return
            }

            if (isTyping.value) {
                clearTimeout(timeoutId)
            }

            isTyping.value = true

            // Начинаем печатать с текущей позиции
            displayedText.value = text.slice(0, startIndex)

            function typeNextCharacter() {
                if (startIndex < text.length && props.enabled) {
                    displayedText.value = text.slice(0, startIndex + 1)
                    startIndex++
                    timeoutId = setTimeout(typeNextCharacter, props.typingSpeed)
                } else {
                    isTyping.value = false
                    emit('complete')
                }
            }

            typeNextCharacter()
        }

        watch(() => props.text, (newText, oldText) => {
            if (newText === oldText) return

            // Очищаем предыдущий таймаут
            if (timeoutId) {
                clearTimeout(timeoutId)
            }

            // Если новый текст включает старый как префикс,
            // продолжаем печатать с места окончания старого текста
            if (oldText && newText.startsWith(oldText)) {
                typeText(newText, oldText.length)
            } else {
                // Только для первого запуска печатаем с начала
                if (!oldText) {
                    displayedText.value = ''
                    typeText(newText, 0)
                }
            }
        }, { immediate: true })

        onBeforeUnmount(() => {
            if (timeoutId) {
                clearTimeout(timeoutId)
            }
            isTyping.value = false
        })

        return () => h('span', { class: 'inline' }, displayedText.value)
    }
})

const props = defineProps({
    message: {
        type: Object,
        required: true
    }
})

const emit = defineEmits(['message-complete'])

// States
const currentGapIndex = ref(0)
const selectedAnswers = ref({})
const wrongAttempts = ref({})
const shouldShowNextPart = ref(false)
const isComplete = ref(false)
const attemptsCount = ref({})

// Computed
const currentGap = computed(() => {
    if (currentGapIndex.value === null || !props.message?.gaps) return null
    return props.message.gaps[currentGapIndex.value]
})

const textBeforeGap = computed(() => {
    if (!currentGap.value) return props.message.text

    const parts = props.message.text.split(`{gap${currentGap.value.id}}`)
    return parts[0]
})

const textAfterGap = computed(() => {
    if (!currentGap.value) return ''

    const parts = props.message.text.split(`{gap${currentGap.value.id}}`)
    if (parts.length < 2) return ''

    const textAfter = parts[1]

    // Если есть следующий gap
    const nextGap = props.message.gaps[currentGapIndex.value + 1]
    if (nextGap) {
        const nextParts = textAfter.split(`{gap${nextGap.id}}`)
        return nextParts[0]
    }

    return textAfter
})

// Methods
function onTypingComplete() {
    shouldShowNextPart.value = false
}

function onAfterGapComplete() {
    if (currentGapIndex.value < props.message.gaps.length - 1) {
        shouldShowNextPart.value = false
    }
}

async function selectAnswer(answer) {
    if (!currentGap.value || isTypingLocked.value) return

    const isCorrect = currentGap.value.correct === answer

    // Увеличиваем счетчик попыток
    attemptsCount.value[currentGap.value.id] = (attemptsCount.value[currentGap.value.id] || 0) + 1

    if (isCorrect) {
        isTypingLocked.value = true
        selectedAnswers.value[currentGap.value.id] = answer

        // Короткая пауза перед показом следующей части
        await new Promise(resolve => setTimeout(resolve, 300))

        // Показываем следующую часть текста
        shouldShowNextPart.value = true

        // Ждем завершения анимации печати
        await new Promise(resolve => setTimeout(resolve, 500))

        if (currentGapIndex.value < props.message.gaps.length - 1) {
            currentGapIndex.value++
            shouldShowNextPart.value = false
        } else {
            // Если это последний gap, показываем кнопку отправки
            await new Promise(resolve => setTimeout(resolve, 300))
            isComplete.value = true
        }
        isTypingLocked.value = false
    } else {
        wrongAttempts.value[currentGap.value.id] = answer

        // После двух неправильных попыток
        if (attemptsCount.value[currentGap.value.id] >= 2) {
            selectedAnswers.value[currentGap.value.id] = currentGap.value.correct
            await new Promise(resolve => setTimeout(resolve, 300))

            shouldShowNextPart.value = true
            await new Promise(resolve => setTimeout(resolve, 500))

            if (currentGapIndex.value < props.message.gaps.length - 1) {
                currentGapIndex.value++
                shouldShowNextPart.value = false
            } else {
                isComplete.value = true
            }
        }
    }
}

function getGapHighlightClass(gapId) {
    if (!gapId) return 'bg-gray-500/20 border border-gray-500'

    if (selectedAnswers.value[gapId]) {
        return 'bg-green-500/20 border border-green-500'
    }
    if (wrongAttempts.value[gapId]) {
        return 'bg-red-500/20 border border-red-500'
    }
    return 'bg-gray-500/20 border border-gray-500'
}

function getOptionClass(gapId, word) {
    if (!gapId) return ''

    const baseClass = themeStore.isDark ? 'bg-dark-primary' : 'bg-light-primary'

    if (selectedAnswers.value[gapId] === word) {
        return `${baseClass} ring-2 ring-green-500 opacity-100`
    }
    if (wrongAttempts.value[gapId] === word) {
        return `${baseClass} ring-2 ring-red-500 opacity-50`
    }
    return `${baseClass} hover:bg-opacity-80`
}

function isOptionDisabled(gapId, word) {
    if (!gapId) return true
    return wrongAttempts.value[gapId] === word || selectedAnswers.value[gapId]
}

// Processed message
const processedMessage = computed(() => {
    let finalText = props.message.text
    let finalTranslation = props.message.translation

    for (const gap of props.message.gaps) {
        const answer = selectedAnswers.value[gap.id]
        if (answer) {
            finalText = finalText.replace(`{gap${gap.id}}`, answer)
            const translation = gap.options.find(o => o.word === answer)?.translation
            if (translation) {
                finalTranslation = finalTranslation.replace(`{gap${gap.id}}`, translation)
            }
        }
    }

    return {
        ...props.message,
        text: finalText,
        translation: finalTranslation
    }
})
</script>

<style scoped>
.inline {
    display: inline;
    white-space: pre-wrap;
}
</style>