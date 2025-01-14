<!-- src/components/WordCard.vue -->
<template>
    <div class="rounded-lg shadow-md transition-all duration-300 hover:shadow-lg cursor-pointer" :class="[
        themeStore.isDark
            ? 'bg-dark-secondary'
            : 'bg-light-secondary'
    ]" @click="openDetailModal">
        <div class="p-6 relative">
            <!-- Избранное и Аудио -->
            <div class="absolute top-4 right-4 flex space-x-2">
                <button @click.stop="toggleFavorite" class="p-2 rounded-full transition-colors" :class="[
                    isFavorite
                        ? (themeStore.isDark
                            ? 'bg-dark-accent text-dark-text'
                            : 'bg-light-accent text-light-text')
                        : (themeStore.isDark
                            ? 'hover:bg-dark-primary/50 text-dark-text/50'
                            : 'hover:bg-light-primary/50 text-light-text/50')
                ]">
                    <BookmarkIcon :class="[
                        'w-5 h-5',
                        isFavorite ? 'fill-current' : 'stroke-current'
                    ]" />
                </button>
                <button @click.stop="playAudio" class="p-2 rounded-full transition-colors" :class="[
                    themeStore.isDark
                        ? 'hover:bg-dark-primary/50 text-dark-text/50'
                        : 'hover:bg-light-primary/50 text-light-text/50'
                ]">
                    <VolumeIcon class="w-5 h-5" />
                </button>
            </div>

            <!-- Основная информация о слове -->
            <div>
                <h3 class="text-xl font-semibold mb-2" :class="[
                    themeStore.isDark ? 'text-dark-text' : 'text-light-text'
                ]">
                    {{ word.word }}
                </h3>
                <p class="text-sm mb-4" :class="[
                    themeStore.isDark ? 'text-dark-text/70' : 'text-light-text/70'
                ]">
                    {{ word.translation }}
                </p>

                <!-- Тип слова и сложность -->
                <div class="flex justify-between items-center">
                    <span class="px-2 py-1 rounded-full text-xs" :class="[
                        themeStore.isDark
                            ? 'bg-dark-primary text-dark-text/70'
                            : 'bg-light-primary text-light-text/70'
                    ]">
                        {{ formatWordType(word.word_type) }}
                    </span>
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
            </div>
        </div>
    </div>

    <!-- Модалка с деталями слова -->
    <WordDetailModal v-if="isDetailModalOpen" :is-open="isDetailModalOpen" :word="word" @close="closeDetailModal" />
</template>

<script setup>
import { ref, computed } from 'vue'
import { BookmarkIcon, VolumeIcon } from 'lucide-vue-next'
import { useWordsStore } from '@/stores/wordsStore'
import { useThemeStore } from '@/stores/themeStore'
import WordDetailModal from './WordDetailModal.vue'

const props = defineProps({
    word: {
        type: Object,
        required: true
    }
})

const wordsStore = useWordsStore()
const themeStore = useThemeStore()

// Состояние модалки
const isDetailModalOpen = ref(false)

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
    try {
        await wordsStore.toggleFavorite(props.word.id)
    } catch (error) {
        console.error('Не удалось добавить в избранное', error)
    }
}

// Воспроизведение аудио
async function playAudio() {
    await wordsStore.fetchWordAudio(props.word.id)
}

// Открытие/закрытие модалки
function openDetailModal() {
    isDetailModalOpen.value = true
}

function closeDetailModal() {
    isDetailModalOpen.value = false
}
</script>