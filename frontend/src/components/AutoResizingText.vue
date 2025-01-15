<!-- src/components/AutoResizingText.vue -->
<template>
    <div ref="container" class="overflow-hidden w-full">
        <div ref="textElement"
            class="whitespace-nowrap text-center transform-origin-center transition-transform duration-200"
            :style="{ transform: `scale(${scale})` }" :class="[
                themeStore.isDark ? 'text-dark-text' : 'text-light-text'
            ]">
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
        required: true
    },
    minScale: {
        type: Number,
        default: 0.3
    },
    maxFontSize: {
        type: Number,
        default: 18 // базовый размер шрифта
    }
})

const themeStore = useThemeStore()
const container = ref(null)
const textElement = ref(null)
const scale = ref(1)

// Функция для расчета масштаба
const calculateScale = async () => {
    if (!container.value || !textElement.value) return

    const containerWidth = container.value.offsetWidth
    const containerHeight = container.value.offsetHeight
    const textWidth = textElement.value.offsetWidth
    const textHeight = textElement.value.offsetHeight

    scale.value = 1
    await nextTick()

    const widthScale = containerWidth / textWidth
    const heightScale = containerHeight / textHeight
    let newScale = Math.min(widthScale, heightScale)
    newScale = Math.max(props.minScale, Math.min(1, newScale))

    scale.value = newScale
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

    // Инициальный расчет
    calculateScale()
})

// Следим за изменением текста
watch(() => props.text, () => {
    nextTick(() => calculateScale())
})

// Очистка при размонтировании
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