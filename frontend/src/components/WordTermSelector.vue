<!-- src/components/WordTermSelector.vue -->
<template>
    <div class="space-y-4">
        <!-- Кнопка Random -->

        <!-- Слова -->
        <div>
            <label class="block text-sm font-medium mb-2"
                :class="[themeStore.isDark ? 'text-dark-text' : 'text-light-text']">
                Слова (до {{ maxWords }})
            </label>
            <div class="flex flex-wrap gap-2">
                <div v-for="i in maxWords" :key="'word-' + i" class="flex-1 min-w-[200px]">
                    <select v-model="selectedWords[i - 1]" class="w-full p-2 rounded-lg transition-colors"
                        :class="[themeStore.isDark ? 'bg-dark-primary text-dark-text' : 'bg-light-primary text-light-text']"
                        @change="onWordSelect(i - 1)">
                        <option value="">Выберите слово</option>
                        <optgroup v-for="(words, type) in groupedWords" :key="type" :label="formatWordType(type)">
                            <option v-for="word in words" :key="word.id" :value="word.word"
                                :disabled="isWordSelected(word.word)">
                                {{ word.word }} ({{ word.translation }})
                            </option>
                        </optgroup>
                    </select>
                </div>
            </div>
        </div>

        <!-- Термины -->
        <div>
            <label class="block text-sm font-medium mb-2"
                :class="[themeStore.isDark ? 'text-dark-text' : 'text-light-text']">
                Термины (до {{ maxTerms }})
            </label>
            <div class="flex flex-wrap gap-2">
                <div v-for="i in maxTerms" :key="'term-' + i" class="flex-1 min-w-[200px]">
                    <select v-model="selectedTerms[i - 1]" class="w-full p-2 rounded-lg transition-colors"
                        :class="[themeStore.isDark ? 'bg-dark-primary text-dark-text' : 'bg-light-primary text-light-text']"
                        @change="onTermSelect(i - 1)">
                        <option value="">Выберите термин</option>
                        <optgroup v-for="(terms, category) in groupedTerms" :key="category" :label="category">
                            <option v-for="term in terms" :key="term.id" :value="term.term"
                                :disabled="isTermSelected(term.term)">
                                {{ term.term }}
                            </option>
                        </optgroup>
                    </select>
                </div>
            </div>
        </div>
        <button @click="selectRandom" class="mb-4 px-4 py-2 rounded-lg font-medium transition-all duration-300" :class="[themeStore.isDark
            ? 'bg-dark-accent text-dark-text hover:bg-dark-accent/90'
            : 'bg-light-accent text-light-text hover:bg-light-accent/90']">
            Случайный выбор
        </button>
    </div>
</template>

<script setup>
import { ref, computed } from 'vue'
import { useThemeStore } from '@/stores/themeStore'

const themeStore = useThemeStore()

const props = defineProps({
    words: {
        type: Array,
        required: true
    },
    terms: {
        type: Array,
        required: true
    },
    maxWords: {
        type: Number,
        default: 3
    },
    maxTerms: {
        type: Number,
        default: 2
    }
})

const emit = defineEmits(['update:selection'])

const selectedWords = ref(Array(props.maxWords).fill(''))
const selectedTerms = ref(Array(props.maxTerms).fill(''))

// Группировка слов по типу
const groupedWords = computed(() => {
    return props.words.reduce((acc, word) => {
        if (!acc[word.word_type]) {
            acc[word.word_type] = []
        }
        acc[word.word_type].push(word)
        return acc
    }, {})
})

// Группировка терминов по категории
const groupedTerms = computed(() => {
    return props.terms.reduce((acc, term) => {
        if (!acc[term.category_main]) {
            acc[term.category_main] = []
        }
        acc[term.category_main].push(term)
        return acc
    }, {})
})

function formatWordType(type) {
    const types = {
        NOUN: 'Существительные',
        VERB: 'Глаголы',
        ADJECTIVE: 'Прилагательные',
        ADVERB: 'Наречия',
        COMMON_PHRASE: 'Фразы'
    }
    return types[type] || type
}

// Добавить новую функцию в <script setup>
function selectRandom() {
    // Случайный выбор слов
    const availableWords = props.words.filter(word => !isWordSelected(word.word))
    const randomWords = []
    for (let i = 0; i < props.maxWords; i++) {
        if (availableWords.length > 0) {
            const randomIndex = Math.floor(Math.random() * availableWords.length)
            randomWords.push(availableWords[randomIndex].word)
            availableWords.splice(randomIndex, 1)
        } else {
            randomWords.push('')
        }
    }
    selectedWords.value = randomWords

    // Случайный выбор терминов
    const availableTerms = props.terms.filter(term => !isTermSelected(term.term))
    const randomTerms = []
    for (let i = 0; i < props.maxTerms; i++) {
        if (availableTerms.length > 0) {
            const randomIndex = Math.floor(Math.random() * availableTerms.length)
            randomTerms.push(availableTerms[randomIndex].term)
            availableTerms.splice(randomIndex, 1)
        } else {
            randomTerms.push('')
        }
    }
    selectedTerms.value = randomTerms

    emitSelection()
}

function isWordSelected(word) {
    return selectedWords.value.includes(word)
}

function isTermSelected(term) {
    return selectedTerms.value.includes(term)
}

function onWordSelect(index) {
    emitSelection()
}

function onTermSelect(index) {
    emitSelection()
}

function emitSelection() {
    emit('update:selection', {
        words: selectedWords.value.filter(Boolean),
        terms: selectedTerms.value.filter(Boolean)
    })
}
</script>