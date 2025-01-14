// frontend/src/router/index.js
import { createRouter, createWebHistory } from 'vue-router'

const router = createRouter({
  history: createWebHistory(import.meta.env.BASE_URL),
  routes: [
    {
      path: '/',
      name: 'home',
      component: () => import('../views/HomePage.vue'),
    },
    {
      path: '/tasks',
      name: 'tasks',
      component: () => import('../views/TasksPage.vue'),
    },
    // {
    //   path: '/terms',
    //   name: 'terms',
    //   component: () => import('../views/TermsPage.vue'),
    // },
    {
      path: '/profile',
      name: 'profile',
      component: () => import('../views/ProfilePage.vue'),
      meta: { requiresAuth: true },
    },
    {
      path: '/auth',
      name: 'auth',
      component: () => import('../views/AuthPage.vue'),
      meta: { requiresGuest: true },
    },
  ],
})

// Защита роутов
router.beforeEach(async (to, from) => {
  // Здесь будет проверка авторизации
  const isAuthenticated = false // Временно, позже будем получать из store

  if (to.meta.requiresAuth && !isAuthenticated) {
    return { name: 'auth' }
  }

  if (to.meta.requiresGuest && isAuthenticated) {
    return { name: 'home' }
  }
})

export default router
