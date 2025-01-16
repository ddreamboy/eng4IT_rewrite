// src/router/index.js
import { createRouter, createWebHistory } from 'vue-router'
import { useAuthStore } from '@/stores/authStore'

const router = createRouter({
  history: createWebHistory(import.meta.env.BASE_URL),
  routes: [
    {
      path: '/',
      name: 'home',
      component: () => import('@/views/HomePage.vue'),
      meta: { requiresAuth: true },
    },
    {
      path: '/auth',
      name: 'auth',
      component: () => import('@/views/AuthPage.vue'),
      meta: { requiresGuest: true },
    },
    {
      path: '/profile',
      name: 'profile',
      component: () => import('@/views/ProfilePage.vue'),
      meta: { requiresAuth: true },
    },
    {
      path: '/dictionary',
      name: 'dictionary',
      component: () => import('@/views/TermsWordsPage.vue'),
      meta: { requiresAuth: true },
    },
    {
      path: '/exercise/term-definition',
      name: 'termDefinition',
      component: () => import('@/views/TermDefinitionExercise.vue'),
      meta: { requiresAuth: true },
    },
    {
      path: '/exercise/word-matching',
      name: 'wordMatching',
      component: () => import('@/views/WordMatchingExercise.vue'),
      meta: { requiresAuth: true },
    },
    {
      path: '/exercise/word-translation',
      name: 'wordTranslation',
      component: () => import('@/views/WordTranslationExercise.vue'),
      meta: { requiresAuth: true },
    },
    {
      path: '/exercise/chat-dialog',
      name: 'chatDialog',
      component: () => import('@/views/ChatDialogExercise.vue'),
      meta: { requiresAuth: true },
    },
  ],
})

router.beforeEach(async (to, from) => {
  const authStore = useAuthStore()
  
  // Проверяем статус авторизации
  if (to.meta.requiresAuth && !authStore.isAuthenticated) {
    // Сохраняем URL для редиректа после авторизации
    return { 
      name: 'auth',
      query: { redirect: to.fullPath }
    }
  }

  if (to.meta.requiresGuest && authStore.isAuthenticated) {
    return { name: 'home' }
  }
})

export default router
