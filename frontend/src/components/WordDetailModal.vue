<!-- src/components/WordDetailModal.vue -->
<template>
    <div v-if="isOpen"
        class="fixed inset-0 z-50 flex items-center justify-center overflow-x-hidden overflow-y-auto outline-none focus:outline-none">
        <!-- Overlay -->
        <div class="fixed inset-0 transition-opacity duration-300" :class="[
            themeStore.isDark
                ? 'bg-dark-primary/50'
                : 'bg-light-primary/50'
        ]" @click="closeModal"></div>

        <!-- Modal Container -->
        <div class="relative w-full max-w-2xl mx-4 my-6 transition-all duration-300 ease-out transform" :class="[
            themeStore.isDark
                ? 'bg-dark-secondary text-dark-text'
                : 'bg-light-secondary text-light-text',
            'rounded-lg shadow-xl'
        ]">
            <!-- Header -->
            <div class="flex items-center justify-between p-6 border-b" :class="[
                themeStore.isDark
                    ? 'border-dark-primary'
                    : 'border-light-primary'
            ]">
                <h3 class="text-2xl font-semibold">
                    {{ word.word }}
                </h3>
                <button @click="closeModal"
                    class="p-2 ml-auto bg-transparent border-0 text-black opacity-5 float-right text-3xl leading-none font-semibold outline-none focus:outline-none">
                    <span class="text-black opacity-5 h-6 w-6 text-2xl block outline-none focus:outline-none">
                        ×
                    </span>
                </button>
            </div>

            <!-- Body -->
            <div class="relative p-6 flex-auto">
                <div class="mb-4">
                    <h4 class="text-lg font-medium mb-2">Перевод</h4>
                    <p>{{ word.translation }}</p>
                </div>

                <div class="mb-4">
                    <h4 class="text-lg font-medium mb-2">Тип слова</h4>
                    <p>{{ formatWordType(word.word_type) }}</p>
                </div>

                <div class="mb-4">
                    <h4 class="text-lg font-medium mb-2">Контекст (EN)</h4>
                    <p class="italic">{{ word.context }}</p>
                </div>

                <div class="mb-4">
                    <h4 class="text-lg font-medium mb-2">Перевод контекста (RU)</h4>
                    <p class="italic">{{ word.context_translation }}</p>
                </div>

                <div class="mb-4 flex items-center justify-between">
                    <div>
                        <h4 class="text-lg font-medium mb-2">Сложность</h4>
                        <span class="px-2 py-1 rounded-full text-xs" :class="[
                            word.difficulty === 'basic'
                                ? 'bg-green-200 text-green-800'
                                : word.difficulty === 'intermediate'
                                    ? 'bg-yellow-200 text-yellow-800'
                                    : 'bg-red-200 text-red-800'
                        ]">
                            {{ formatDifficulty(word.difficulty) }}
                        </span>
                    </div>

                    <!-- Кнопки действий -->
                    <div class="flex space-x-2">
                        <button @click="playAudio" class="p-2 rounded-full transition-colors" :class="[
                            themeStore.isDark
                                ? 'hover:bg-dark-primary/50 text-dark-text/50'
                                : 'hover:bg-light-primary/50 text-light-text/50'
                        ]">
                            <VolumeIcon class="w-6 h-6" />
                        </button>
                        <button @click="toggleFavorite" class="p-2 rounded-full transition-colors" :class="[
                            isFavorite
                                ? (themeStore.isDark
                                    ? 'bg-dark-accent text-dark-text'
                                    : 'bg-light-accent text-light-text')
                                : (themeStore.isDark
                                    ? 'hover:bg-dark-primary/50 text-dark-text/50'
                                    : 'hover:bg-light-primary/50 text-light-text/50')
                        ]">
                            <BookmarkIcon :class="[
                                'w-6 h-6',
                                isFavorite ? 'fill-current' : 'stroke-current'
                            ]" />
                        </button>
                    </div>
                </div>
            </div>

            <!-- Footer -->
            <div class="flex items-center justify-end p-6 border-t" :class="[
                themeStore.isDark
                    ? 'border-dark-primary'
                    : 'border-light-primary'
            ]">
                <button @click="closeModal" class="px-4 py-2 rounded-lg transition-colors" :class="[
                    themeStore.isDark
                        ? 'bg-dark-accent text-dark-text hover:bg-dark-accent/90'
                        : 'bg-light-accent text-light-text hover:bg-light-accent/90'
                ]">
                    Закрыть
                </button>
            </div>
        </div>
    </div>
</template>

<script setup>
import { computed } from 'vue'
import { BookmarkIcon, VolumeIcon } from 'lucide-vue-next'
import { useWordsStore } from '@/stores/wordsStore'
import { useThemeStore } from '@/stores/themeStore'

const props = defineProps({
    isOpen: {
        type: Boolean,
        required: true
    },
    word: {
        type: Object,
        required: true
    }
})

const emit = defineEmits(['close'])

const wordsStore = useWordsStore()
const themeStore = useThemeStore()

// Проверка избранного
const isFavorite = computed(() =>
    wordsStore.favorites.includes(props.word.id)
)

// Форматирование сложности
function formatDifficulty(difficulty) {
    const difficulties = {
        'beginner': 'Начинающий',
        'basic': 'Базовый',
        'intermediate': 'Средний',
        'advanced': 'Сложный'
    }
    return difficulties[difficulty] || difficulty
}

// Форматирование типа слова
function formatWordType(type) {
    const types = {
        'NOUN': 'Существительное',
        'VERB': 'Глагол',
        'ADJECTIVE': 'Прилагательное',
        'ADVERB': 'Наречие'
    }
    return types[type] || type
}

// Добавление/удаление из избранного
async function toggleFavorite() {
    await wordsStore.toggleFavorite(props.word.id)
}

// Воспроизведение аудио
async function playAudio() {
    await wordsStore.fetchWordAudio(props.word.id)
}

// Закрытие модалки
function closeModal() {
    emit('close')
}
</script>