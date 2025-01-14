<!-- src/components/TermCard.vue -->
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

            <!-- Основная информация о термине -->
            <div>
                <h3 class="text-xl font-semibold mb-2" :class="[
                    themeStore.isDark ? 'text-dark-text' : 'text-light-text'
                ]">
                    {{ term.term }}
                </h3>
                <p class="text-sm mb-4" :class="[
                    themeStore.isDark ? 'text-dark-text/70' : 'text-light-text/70'
                ]">
                    {{ term.primary_translation }}
                </p>

                <!-- Категория и сложность -->
                <div class="flex justify-between items-center">
                    <span class="px-2 py-1 rounded-full text-xs" :class="[
                        themeStore.isDark
                            ? 'bg-dark-primary text-dark-text/70'
                            : 'bg-light-primary text-light-text/70'
                    ]">
                        {{ term.category_main }}
                    </span>
                    <span class="px-2 py-1 rounded-full text-xs" :class="[
                        term.difficulty === 'basic'
                            ? 'bg-green-200 text-green-800'
                            : term.difficulty === 'intermediate'
                                ? 'bg-yellow-200 text-yellow-800'
                                : 'bg-red-200 text-red-800'
                    ]">
                        {{ formatDifficulty(term.difficulty) }}
                    </span>
                </div>
            </div>
        </div>
    </div>

    <!-- Модалка с деталями термина -->
    <TermDetailModal :is-open="isDetailModalOpen" :term="term" @close="closeDetailModal" />
</template>

<script setup>
import { ref, computed } from 'vue'
import { BookmarkIcon, VolumeIcon } from 'lucide-vue-next'
import { useTermsStore } from '@/stores/termsStore'
import { useThemeStore } from '@/stores/themeStore'
import TermDetailModal from './TermDetailModal.vue'

const props = defineProps({
  term: {
    type: Object,
    required: true
  }
})

const termsStore = useTermsStore()
const themeStore = useThemeStore()

// Состояние модалки
const isDetailModalOpen = ref(false)

// Проверка избранного
const isFavorite = computed(() => 
  termsStore.favorites.includes(props.term.id)
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

// Добавление/удаление из избранного
async function toggleFavorite() {
  try {
    await termsStore.toggleFavorite(props.term.id)
  } catch (error) {
    console.error('Не удалось добавить в избранное', error)
  }
}

// Воспроизведение аудио
async function playAudio() {
  await termsStore.fetchTermAudio(props.term.id)
}

// Открытие/закрытие модалки
function openDetailModal() {
  isDetailModalOpen.value = true
}

function closeDetailModal() {
  isDetailModalOpen.value = false
}
</script>