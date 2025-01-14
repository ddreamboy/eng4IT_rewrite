<!-- src/components/tasks/DevModePanel.vue -->
<template>
    <div class="p-4 rounded-lg bg-yellow-50 dark:bg-yellow-900/20 border border-yellow-200 dark:border-yellow-700">
      <div class="flex items-center justify-between mb-4">
        <h3 class="text-lg font-semibold text-yellow-800 dark:text-yellow-200">
          Режим разработчика
        </h3>
        <div class="space-x-2">
          <button
            @click="loadTemplate"
            class="px-3 py-1.5 text-sm rounded-lg bg-light-primary/10 dark:bg-dark-primary/10"
          >
            Загрузить шаблон
          </button>
          <button
            @click="saveTemplate"
            class="px-3 py-1.5 text-sm rounded-lg bg-light-primary/10 dark:bg-dark-primary/10"
          >
            Сохранить шаблон
          </button>
        </div>
      </div>
  
      <!-- JSON редактор -->
      <div class="space-y-2">
        <label class="block text-sm font-medium">
          Параметры запроса (JSON)
        </label>
        <textarea
          v-model="jsonParams"
          rows="10"
          class="w-full p-3 font-mono text-sm rounded-lg bg-light-primary/5 dark:bg-dark-primary/5 
                 border border-light-primary/10 dark:border-dark-primary/10"
          :class="{ 'border-red-500': jsonError }"
          @input="validateJson"
        ></textarea>
        <p v-if="jsonError" class="text-sm text-red-500">
          {{ jsonError }}
        </p>
      </div>
  
      <!-- Предпросмотр запроса -->
      <div class="mt-4 space-y-2">
        <h4 class="text-sm font-medium">Итоговый запрос:</h4>
        <pre class="p-3 rounded-lg bg-gray-100 dark:bg-gray-800 overflow-auto text-xs">
  {{ finalRequest }}</pre>
      </div>
  
      <!-- Кнопка генерации -->
      <div class="mt-4 flex justify-end">
        <button
          @click="generateTask"
          :disabled="!!jsonError"
          class="px-4 py-2 text-white rounded-lg bg-light-accent dark:bg-dark-accent
                 disabled:opacity-50 disabled:cursor-not-allowed"
        >
          Сгенерировать задание
        </button>
      </div>
    </div>
  
    <!-- Модальное окно для шаблонов -->
    <Dialog :open="isTemplateModalOpen" @close="isTemplateModalOpen = false">
      <DialogPanel class="w-full max-w-md p-6 rounded-lg bg-light-secondary dark:bg-dark-secondary">
        <DialogTitle class="text-lg font-medium mb-4">
          {{ isLoadingTemplate ? 'Загрузить шаблон' : 'Сохранить шаблон' }}
        </DialogTitle>
  
        <div class="space-y-4">
          <div v-if="isLoadingTemplate">
            <!-- Список сохраненных шаблонов -->
            <label class="block text-sm font-medium mb-2">Выберите шаблон</label>
            <select
              v-model="selectedTemplate"
              class="w-full p-2 rounded-lg bg-light-primary/5 dark:bg-dark-primary/5 
                     border border-light-primary/10 dark:border-dark-primary/10"
            >
              <option v-for="template in savedTemplates" :key="template.name" :value="template">
                {{ template.name }}
              </option>
            </select>
          </div>
          <div v-else>
            <!-- Форма сохранения шаблона -->
            <label class="block text-sm font-medium mb-2">Название шаблона</label>
            <input
              v-model="templateName"
              type="text"
              class="w-full p-2 rounded-lg bg-light-primary/5 dark:bg-dark-primary/5 
                     border border-light-primary/10 dark:border-dark-primary/10"
              placeholder="Мой шаблон"
            >
          </div>
        </div>
  
        <div class="mt-6 flex justify-end space-x-3">
          <button
            @click="isTemplateModalOpen = false"
            class="px-4 py-2 rounded-lg bg-light-primary/10 dark:bg-dark-primary/10"
          >
            Отмена
          </button>
          <button
            @click="isLoadingTemplate ? loadSelectedTemplate() : saveCurrentTemplate()"
            class="px-4 py-2 text-white rounded-lg bg-light-accent dark:bg-dark-accent"
          >
            {{ isLoadingTemplate ? 'Загрузить' : 'Сохранить' }}
          </button>
        </div>
      </DialogPanel>
    </Dialog>
  </template>
  
  <script setup>
  import { ref, computed } from 'vue'
  import { Dialog, DialogPanel, DialogTitle } from '@headlessui/vue'
  
  const props = defineProps({
    selectedType: {
      type: String,
      required: true
    },
    modelValue: {
      type: Object,
      required: true
    }
  })
  
  const emit = defineEmits(['update:modelValue', 'generate'])
  
  // JSON редактор
  const jsonParams = ref(JSON.stringify(props.modelValue, null, 2))
  const jsonError = ref('')
  
  // Модальное окно шаблонов
  const isTemplateModalOpen = ref(false)
  const isLoadingTemplate = ref(false)
  const templateName = ref('')
  const selectedTemplate = ref(null)
  
  // Загружаем сохраненные шаблоны из localStorage
  const savedTemplates = computed(() => {
    const templates = localStorage.getItem('taskTemplates')
    return templates ? JSON.parse(templates) : []
  })
  
  // Валидация JSON
  function validateJson(event) {
    const value = event.target.value
    try {
      const parsed = JSON.parse(value)
      jsonError.value = ''
      emit('update:modelValue', parsed)
    } catch (error) {
      jsonError.value = 'Некорректный JSON: ' + error.message
    }
  }
  
  // Предпросмотр запроса
  const finalRequest = computed(() => {
    const request = {
      url: `/api/v1/tasks/generate/${props.selectedType}`,
      method: 'POST',
      params: jsonError.value ? props.modelValue : JSON.parse(jsonParams.value)
    }
    return JSON.stringify(request, null, 2)
  })
  
  // Генерация задания
  function generateTask() {
    if (!jsonError.value) {
      const params = JSON.parse(jsonParams.value)
      emit('generate', params)
    }
  }
  
  // Работа с шаблонами
  function loadTemplate() {
    isLoadingTemplate.value = true
    isTemplateModalOpen.value = true
  }
  
  function saveTemplate() {
    isLoadingTemplate.value = false
    isTemplateModalOpen.value = true
    templateName.value = ''
  }
  
  function loadSelectedTemplate() {
    if (selectedTemplate.value) {
      jsonParams.value = JSON.stringify(selectedTemplate.value.params, null, 2)
      validateJson({ target: { value: jsonParams.value } })
    }
    isTemplateModalOpen.value = false
  }
  
  function saveCurrentTemplate() {
    if (!templateName.value || jsonError.value) return
  
    const templates = savedTemplates.value
    const template = {
      name: templateName.value,
      type: props.selectedType,
      params: JSON.parse(jsonParams.value),
      created: new Date().toISOString()
    }
  
    // Добавляем или обновляем шаблон
    const index = templates.findIndex(t => t.name === templateName.value)
    if (index !== -1) {
      templates[index] = template
    } else {
      templates.push(template)
    }
  
    localStorage.setItem('taskTemplates', JSON.stringify(templates))
    isTemplateModalOpen.value = false
  }
  
  // Следим за изменениями props.modelValue
  watch(() => props.modelValue, (newValue) => {
    if (JSON.stringify(newValue) !== jsonParams.value) {
      jsonParams.value = JSON.stringify(newValue, null, 2)
    }
  }, { deep: true })
  </script>
  
  <style scoped>
  /* ...existing styles... */
  </style>