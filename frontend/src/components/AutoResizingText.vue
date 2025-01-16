// src/components/AutoResizingText.vue
<template>
    <div ref="container" class="overflow-hidden flex items-center justify-center" :class="[
        containerClass,
        fullWidth ? 'w-full' : '',
        minHeight ? `min-h-[${minHeight}px]` : ''
    ]">
        <div ref="textElement"
            class="text-center transform-origin-center transition-transform duration-200 break-words whitespace-pre-wrap"
            :style="{
                transform: `scale(${scale})`,
                maxWidth: '100%',
                wordBreak: 'break-word',
                fontSize: `${fontSize}px`,
                lineHeight: lineHeight
            }" :class="[themeStore.isDark ? 'text-dark-text' : 'text-light-text']">
            {{ text }}
        </div>
    </div>
</template>

<script setup>
import { ref, onMounted, onBeforeUnmount, watch, nextTick } from 'vue'
import { useThemeStore } from '@/stores/themeStore'

const props = defineProps({
    text: {
        type: String,
        required: true,
    },
    minScale: {
        type: Number,
        default: 0.3,
    },
    maxFontSize: {
        type: Number,
        default: 18,
    },
    // Новые пропсы для гибкости
    fullWidth: {
        type: Boolean,
        default: false,
    },
    minHeight: {
        type: Number,
        default: null,
    },
    containerClass: {
        type: String,
        default: '',
    },
    lineHeight: {
        type: String,
        default: '1.5',
    }
})

const themeStore = useThemeStore()
const container = ref(null)
const textElement = ref(null)
const scale = ref(1)
const fontSize = ref(props.maxFontSize)

// Функция для расчета масштаба
const calculateScale = async () => {
    if (!container.value || !textElement.value) return

    // Сначала пробуем уместить текст с переносами
    fontSize.value = props.maxFontSize
    scale.value = 1
    await nextTick()

    const containerWidth = container.value.offsetWidth
    const containerHeight = container.value.offsetHeight
    let textWidth = textElement.value.offsetWidth
    let textHeight = textElement.value.offsetHeight

    // Если текст не помещается даже с переносами, уменьшаем размер шрифта
    while ((textWidth > containerWidth || textHeight > containerHeight) && fontSize.value > 8) {
        fontSize.value -= 1
        await nextTick()
        textWidth = textElement.value.offsetWidth
        textHeight = textElement.value.offsetHeight
    }

    // Если все еще не помещается, применяем масштабирование
    if (textWidth > containerWidth || textHeight > containerHeight) {
        const widthScale = containerWidth / textWidth
        const heightScale = containerHeight / textHeight
        let newScale = Math.min(widthScale, heightScale)
        newScale = Math.max(props.minScale, Math.min(1, newScale))
        scale.value = newScale
    }
}

// Наблюдатель размера
let resizeObserver
onMounted(() => {
    if (container.value) {
        resizeObserver = new ResizeObserver(() => {
            calculateScale()
        })
        resizeObserver.observe(container.value)
    }
    calculateScale()
})

watch(
    () => props.text,
    () => {
        nextTick(() => calculateScale())
    }
)

onBeforeUnmount(() => {
    if (resizeObserver && container.value) {
        resizeObserver.unobserve(container.value)
        resizeObserver.disconnect()
    }
})
</script>

<style scoped>
.transform-origin-center {
    transform-origin: center;
}
</style>