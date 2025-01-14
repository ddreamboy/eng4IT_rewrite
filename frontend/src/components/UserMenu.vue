<!-- frontend/src/components/UserMenu.vue -->
<template>
  <Menu as="div" class="relative">
    <!-- Аватар/кнопка меню -->
    <MenuButton
      class="flex items-center justify-center w-8 h-8 rounded-full focus:outline-none"
      :class="
        authStore.isAuthenticated
          ? 'bg-light-accent dark:bg-dark-accent'
          : 'bg-light-secondary dark:bg-dark-secondary'
      "
    >
      <span v-if="authStore.isAuthenticated" class="text-sm font-medium text-white">
        {{ authStore.userInitials }}
      </span>
      <User v-else class="w-5 h-5 text-light-accent dark:text-dark-accent" />
    </MenuButton>

    <transition
      enter-active-class="transition duration-100 ease-out"
      enter-from-class="transform scale-95 opacity-0"
      enter-to-class="transform scale-100 opacity-100"
      leave-active-class="transition duration-75 ease-in"
      leave-from-class="transform scale-100 opacity-100"
      leave-to-class="transform scale-95 opacity-0"
    >
      <MenuItems
        class="absolute right-0 mt-2 w-48 origin-top-right rounded-md bg-light-secondary dark:bg-dark-secondary shadow-lg ring-1 ring-black ring-opacity-5 focus:outline-none"
      >
        <div class="py-1">
          <!-- Меню для авторизованного пользователя -->
          <template v-if="authStore.isAuthenticated">
            <MenuItem v-slot="{ active }">
              <RouterLink
                to="/profile"
                :class="[
                  active ? 'bg-light-primary/50 dark:bg-dark-primary/50' : '',
                  'block px-4 py-2 text-sm',
                ]"
              >
                Профиль
              </RouterLink>
            </MenuItem>
            <MenuItem v-slot="{ active }">
              <RouterLink
                to="/settings"
                :class="[
                  active ? 'bg-light-primary/50 dark:bg-dark-primary/50' : '',
                  'block px-4 py-2 text-sm',
                ]"
              >
                Настройки
              </RouterLink>
            </MenuItem>
            <div class="border-t border-light-primary/10 dark:border-dark-primary/10" />
            <MenuItem v-slot="{ active }">
              <button
                @click="handleLogout"
                :class="[
                  active ? 'bg-light-primary/50 dark:bg-dark-primary/50' : '',
                  'block w-full text-left px-4 py-2 text-sm text-red-600 dark:text-red-400',
                ]"
              >
                Выйти
              </button>
            </MenuItem>
          </template>

          <!-- Меню для гостя -->
          <template v-else>
            <MenuItem v-slot="{ active }">
              <RouterLink
                to="/auth"
                :class="[
                  active ? 'bg-light-primary/50 dark:bg-dark-primary/50' : '',
                  'block px-4 py-2 text-sm',
                ]"
              >
                Войти
              </RouterLink>
            </MenuItem>
          </template>
        </div>
      </MenuItems>
    </transition>
  </Menu>
</template>

<script setup>
import { Menu, MenuButton, MenuItems, MenuItem } from '@headlessui/vue'
import { User } from 'lucide-vue-next'
import { useRouter } from 'vue-router'
import { useAuthStore } from '../stores/authStore'

const router = useRouter()
const authStore = useAuthStore()

async function handleLogout() {
  authStore.logout()
  await router.push('/auth')
}
</script>
