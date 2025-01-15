<!-- src/components/TermDetailModal.vue -->
<template>
  <div
    v-if="isOpen"
    class="fixed inset-0 z-50 flex items-center justify-center overflow-x-hidden overflow-y-auto outline-none focus:outline-none"
  >
    <!-- Overlay -->
    <div
      class="fixed inset-0 transition-opacity duration-300"
      :class="[themeStore.isDark ? 'bg-dark-primary/50' : 'bg-light-primary/50']"
      @click="closeModal"
    ></div>

    <!-- Modal Container -->
    <div
      class="relative w-full max-w-2xl mx-4 my-6 transition-all duration-300 ease-out transform"
      :class="[
        themeStore.isDark
          ? 'bg-dark-secondary text-dark-text'
          : 'bg-light-secondary text-light-text',
        'rounded-lg shadow-xl',
      ]"
    >
      <!-- Header -->
      <div
        class="flex items-center justify-between p-6 border-b"
        :class="[themeStore.isDark ? 'border-dark-primary' : 'border-light-primary']"
      >
        <h3 class="text-2xl font-semibold">
          {{ term.term }}
        </h3>
        <button
          @click="closeModal"
          class="p-2 ml-auto bg-transparent border-0 text-black opacity-5 float-right text-3xl leading-none font-semibold outline-none focus:outline-none"
        >
          <span class="text-black opacity-5 h-6 w-6 text-2xl block outline-none focus:outline-none">
            ×
          </span>
        </button>
      </div>

      <!-- Body -->
      <div class="relative p-6 flex-auto">
        <div class="mb-4">
          <h4 class="text-lg font-medium mb-2">Перевод</h4>
          <p>{{ term.primary_translation }}</p>
        </div>

        <div class="mb-4">
          <h4 class="text-lg font-medium mb-2">Категория</h4>
          <p>{{ term.category_main }} - {{ term.category_sub }}</p>
        </div>

        <div class="mb-4">
          <h4 class="text-lg font-medium mb-2">Определение (EN)</h4>
          <p>{{ term.definition_en }}</p>
        </div>

        <div class="mb-4">
          <h4 class="text-lg font-medium mb-2">Определение (RU)</h4>
          <p>{{ term.definition_ru }}</p>
        </div>

        <div class="mb-4">
          <h4 class="text-lg font-medium mb-2">Пример использования (EN)</h4>
          <p>{{ term.example_en }}</p>
        </div>

        <div v-if="term.related_terms && term.related_terms.length">
          <h4 class="text-lg font-medium mb-2">Связанные термины</h4>
          <div class="flex flex-wrap gap-2">
            <span
              v-for="relatedTerm in term.related_terms"
              :key="relatedTerm"
              class="px-2 py-1 rounded-full text-xs"
              :class="[
                themeStore.isDark
                  ? 'bg-dark-primary text-dark-text'
                  : 'bg-light-primary text-light-text',
              ]"
            >
              {{ relatedTerm }}
            </span>
          </div>
        </div>
      </div>

      <!-- Footer -->
      <div
        class="flex items-center justify-end p-6 border-t"
        :class="[themeStore.isDark ? 'border-dark-primary' : 'border-light-primary']"
      >
        <button
          @click="closeModal"
          class="px-4 py-2 rounded-lg transition-colors"
          :class="[
            themeStore.isDark
              ? 'bg-dark-accent text-dark-text hover:bg-dark-accent/90'
              : 'bg-light-accent text-light-text hover:bg-light-accent/90',
          ]"
        >
          Закрыть
        </button>
      </div>
    </div>
  </div>
</template>

<script setup>
import { useThemeStore } from '@/stores/themeStore'

const props = defineProps({
  isOpen: {
    type: Boolean,
    required: true,
  },
  term: {
    type: Object,
    required: true,
  },
})

const emit = defineEmits(['close'])

const themeStore = useThemeStore()

function closeModal() {
  emit('close')
}
</script>
