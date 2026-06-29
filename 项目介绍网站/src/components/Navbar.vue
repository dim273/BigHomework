<script setup lang="ts">
import { computed } from 'vue'
import { storeToRefs } from 'pinia'
import { useWindowScroll } from '@vueuse/core'
import { useAppStore } from '@/stores/app'
import { useTheme } from '@/composables/useTheme'
import logoImg from '@/assets/pic/logo.png'

const appStore = useAppStore()
const { isMenuOpen } = storeToRefs(appStore)
const { isDark, toggleDark } = useTheme()

// 滚动监听：滚动后增加玻璃模糊与阴影
const { y } = useWindowScroll()
const isScrolled = computed(() => y.value > 8)

const links = [
  { name: 'home', label: '首页' },
  { name: 'projects', label: '功能模块' },
  { name: 'about', label: '关于项目' },
] as const
</script>

<template>
  <header
    class="sticky top-0 z-50 transition-all duration-300"
    :class="
      isScrolled
        ? 'glass border-b border-slate-200/60 shadow-soft dark:border-slate-800/60'
        : 'border-b border-transparent bg-transparent'
    "
  >
    <nav class="max-w-6xl mx-auto flex items-center justify-between px-4 py-3.5">
      <!-- Logo -->
      <RouterLink
        to="/"
        class="flex items-center gap-2 text-lg font-extrabold tracking-tight"
        @click="appStore.closeMenu"
      >
        <span class="flex h-8 w-8 items-center justify-center overflow-hidden rounded-lg bg-gradient-to-br from-indigo-500 to-violet-600 shadow-glow">
          <img :src="logoImg" alt="logo" class="h-full w-full object-cover" />
        </span>
        <span class="text-slate-900 dark:text-white">code-assistant-live2d<span class="text-gradient"> 心流编程</span></span>
      </RouterLink>

      <!-- 桌面导航 -->
      <div class="hidden items-center gap-1 md:flex">
        <RouterLink
          v-for="link in links"
          :key="link.name"
          :to="{ name: link.name }"
          class="rounded-lg px-3.5 py-2 text-sm font-medium text-slate-600 transition hover:bg-slate-100/80 hover:text-slate-900 dark:text-slate-300 dark:hover:bg-slate-800/80 dark:hover:text-white"
          active-class="!text-indigo-600 dark:!text-indigo-400 bg-indigo-50/80 dark:bg-indigo-950/40"
        >
          {{ link.label }}
        </RouterLink>
        <button
          type="button"
          class="ml-2 flex h-9 w-9 items-center justify-center rounded-lg border border-slate-200 text-slate-500 transition hover:bg-slate-100 hover:text-slate-900 dark:border-slate-700 dark:text-slate-400 dark:hover:bg-slate-800 dark:hover:text-white"
          :aria-label="isDark ? '切换到浅色模式' : '切换到深色模式'"
          @click="toggleDark()"
        >
          <svg v-if="isDark" xmlns="http://www.w3.org/2000/svg" class="h-4.5 w-4.5" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><circle cx="12" cy="12" r="4"/><path d="M12 2v2M12 20v2M4.93 4.93l1.41 1.41M17.66 17.66l1.41 1.41M2 12h2M20 12h2M6.34 17.66l-1.41 1.41M19.07 4.93l-1.41 1.41"/></svg>
          <svg v-else xmlns="http://www.w3.org/2000/svg" class="h-4.5 w-4.5" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M21 12.79A9 9 0 1 1 11.21 3 7 7 0 0 0 21 12.79z"/></svg>
        </button>
      </div>

      <!-- 移动端汉堡按钮 -->
      <button
        type="button"
        class="flex h-9 w-9 items-center justify-center rounded-lg border border-slate-200 text-slate-600 md:hidden dark:border-slate-700 dark:text-slate-300"
        :aria-expanded="isMenuOpen"
        aria-label="切换菜单"
        @click="appStore.toggleMenu"
      >
        <svg xmlns="http://www.w3.org/2000/svg" class="h-5 w-5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
          <path
            v-if="!isMenuOpen"
            stroke-linecap="round"
            stroke-linejoin="round"
            stroke-width="2"
            d="M4 6h16M4 12h16M4 18h16"
          />
          <path
            v-else
            stroke-linecap="round"
            stroke-linejoin="round"
            stroke-width="2"
            d="M6 18L18 6M6 6l12 12"
          />
        </svg>
      </button>
    </nav>

    <!-- 移动端下拉菜单 -->
    <Transition name="fade">
      <div v-if="isMenuOpen" class="glass border-t border-slate-200/60 md:hidden dark:border-slate-800/60">
        <div class="space-y-0.5 px-4 py-3">
          <RouterLink
            v-for="link in links"
            :key="link.name"
            :to="{ name: link.name }"
            class="block rounded-lg px-3.5 py-2.5 text-base font-medium text-slate-700 transition hover:bg-slate-100 dark:text-slate-200 dark:hover:bg-slate-800"
            active-class="bg-indigo-50 text-indigo-600 dark:bg-indigo-950/40 dark:text-indigo-400"
            @click="appStore.closeMenu"
          >
            {{ link.label }}
          </RouterLink>
          <button
            type="button"
            class="flex w-full items-center gap-2 rounded-lg px-3.5 py-2.5 text-left text-base font-medium text-slate-700 hover:bg-slate-100 dark:text-slate-200 dark:hover:bg-slate-800"
            @click="toggleDark()"
          >
            {{ isDark ? '🌙 深色模式' : '☀️ 浅色模式' }}
          </button>
        </div>
      </div>
    </Transition>
  </header>
</template>
