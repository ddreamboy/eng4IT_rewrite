
<template>
  <div>
    <!-- Ваш шаблон для компонента ItemSelector -->
    <label class="block mb-2 text-sm font-medium">Выберите элемент</label>
    <select v-model="selectedItem" @change="emitSelection" class="w-full p-2 border rounded">
      <option v-for="item in items" :key="item.value" :value="item.value">
        {{ item.label }}
      </option>
    </select>
  </div>
</template>

<script setup>
import { ref, watch } from 'vue'

const props = defineProps({
  modelValue: {
    type: Array,
    default: () => [],
  },
  type: {
    type: String,
    required: true,
  },
  category: {
    type: String,
    default: '',
  },
  wordType: {
    type: String,
    default: '',
  },
})

const emit = defineEmits(['update:modelValue'])

const selectedItem = ref('')

const items = ref([])

// Загрузка элементов на основе типа, категории и типа слова
// TODO: Замените на вызов API при необходимости
watch(
  () => [props.type, props.category, props.wordType],
  () => {
    // Пример заполнения элементов
    if (props.type === 'chat-dialog') {
      items.value = [
        { value: 'term1', label: 'Термин 1' },
        { value: 'term2', label: 'Термин 2' },
      ]
    } else if (props.type === 'email-structure') {
      items.value = [
        { value: 'email1', label: 'Email 1' },
        { value: 'email2', label: 'Email 2' },
      ]
    } else {
      items.value = []
    }
  },
  { immediate: true }
)

function emitSelection() {
  emit('update:modelValue', [...props.modelValue, { type: props.type, value: selectedItem.value }])
  selectedItem.value = ''
}
</script>

<style scoped>
/* Стили для компонента ItemSelector */
</style>