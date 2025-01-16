<template>
    <TransitionRoot appear :show="isOpen" as="template">
        <Dialog as="div" @close="handleClose" class="relative z-50">
            <!-- Backdrop -->
            <TransitionChild enter="duration-300 ease-out" enter-from="opacity-0" enter-to="opacity-100"
                leave="duration-200 ease-in" leave-from="opacity-100" leave-to="opacity-0">
                <div class="fixed inset-0 bg-black/50" />
            </TransitionChild>

            <!-- Modal -->
            <div class="fixed inset-0 overflow-y-auto">
                <div class="flex min-h-full items-center justify-center p-4">
                    <TransitionChild enter="duration-300 ease-out" enter-from="opacity-0 scale-95"
                        enter-to="opacity-100 scale-100" leave="duration-200 ease-in" leave-from="opacity-100 scale-100"
                        leave-to="opacity-0 scale-95">
                        <DialogPanel class="w-full max-w-md p-6 rounded-lg shadow-xl transition-all"
                            :class="[themeStore.isDark ? 'bg-dark-secondary' : 'bg-light-secondary']">
                            <DialogTitle as="h3" class="text-2xl font-bold mb-4"
                                :class="[themeStore.isDark ? 'text-dark-text' : 'text-light-text']">
                                Level {{ level }} Complete!
                            </DialogTitle>

                            <!-- Статистика уровня -->
                            <div class="mb-6 space-y-4">
                                <!-- Счет -->
                                <div class="text-center">
                                    <p class="text-4xl font-bold mb-2"
                                        :class="[themeStore.isDark ? 'text-dark-text' : 'text-light-text']">
                                        +{{ stats.score }}
                                    </p>
                                    <p class="text-sm"
                                        :class="[themeStore.isDark ? 'text-dark-text/70' : 'text-light-text/70']">
                                        Points earned
                                    </p>
                                </div>

                                <!-- Множители -->
                                <div class="grid grid-cols-2 gap-4">
                                    <div class="p-3 rounded-lg" :class="[
                                        themeStore.isDark ? 'bg-dark-primary' : 'bg-light-primary'
                                    ]">
                                        <div class="text-sm opacity-70">Time Bonus</div>
                                        <div class="font-bold">×{{ stats.multipliers.time.toFixed(2) }}</div>
                                    </div>
                                    <div class="p-3 rounded-lg" :class="[
                                        themeStore.isDark ? 'bg-dark-primary' : 'bg-light-primary'
                                    ]">
                                        <div class="text-sm opacity-70">Accuracy</div>
                                        <div class="font-bold">×{{ stats.multipliers.accuracy.toFixed(2) }}</div>
                                    </div>
                                </div>

                                <!-- Детальная статистика -->
                                <div class="space-y-2 p-4 rounded-lg" :class="[
                                    themeStore.isDark ? 'bg-dark-primary' : 'bg-light-primary'
                                ]">
                                    <div class="flex justify-between">
                                        <span class="opacity-70">Time</span>
                                        <span>{{ formatTime(stats.timeSpent) }}</span>
                                    </div>
                                    <div class="flex justify-between">
                                        <span class="opacity-70">Accuracy</span>
                                        <span>{{ (stats.accuracy * 100).toFixed(1) }}%</span>
                                    </div>
                                    <div class="flex justify-between">
                                        <span class="opacity-70">Lives Left</span>
                                        <span>{{ lives }}/3</span>
                                    </div>
                                </div>
                            </div>

                            <!-- Кнопки действий -->
                            <div class="flex justify-between">
                                <button @click="$emit('save-and-exit')"
                                    class="px-4 py-2 rounded-lg font-medium transition-all duration-300" :class="[
                                        themeStore.isDark
                                            ? 'bg-dark-primary text-dark-text hover:bg-dark-primary/90'
                                            : 'bg-light-primary text-light-text hover:bg-light-primary/90',
                                    ]">
                                    Save & Exit
                                </button>
                                <button @click="$emit('continue')"
                                    class="px-4 py-2 rounded-lg font-medium transition-all duration-300" :class="[
                                        themeStore.isDark
                                            ? 'bg-dark-accent text-dark-text hover:bg-dark-accent/90'
                                            : 'bg-light-accent text-light-text hover:bg-light-accent/90',
                                    ]">
                                    Continue
                                </button>
                            </div>
                        </DialogPanel>
                    </TransitionChild>
                </div>
            </div>
        </Dialog>
    </TransitionRoot>
</template>

<script setup>
import { TransitionRoot, TransitionChild, Dialog, DialogPanel, DialogTitle } from '@headlessui/vue'
import { useThemeStore } from '@/stores/themeStore'

const themeStore = useThemeStore()

defineProps({
    isOpen: Boolean,
    level: Number,
    stats: Object,
    lives: Number
})

defineEmits(['continue', 'save-and-exit', 'close'])

function formatTime(seconds) {
    const minutes = Math.floor(seconds / 60)
    const remainingSeconds = seconds % 60
    return `${minutes}:${remainingSeconds.toString().padStart(2, '0')}`
}

function handleClose() {
    // Предотвращаем закрытие по клику вне модального окна
}
</script>