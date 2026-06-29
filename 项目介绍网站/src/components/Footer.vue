<script setup lang="ts">
import { profile } from '@/assets/data/profile'

const year = new Date().getFullYear()

const links = [
  { name: 'home', label: '首页' },
  { name: 'projects', label: '功能模块' },
  { name: 'about', label: '关于项目' },
] as const
</script>

<template>
  <footer class="border-t border-slate-200/70 bg-slate-50/50 dark:border-slate-800/70 dark:bg-slate-950/50">
    <div class="max-w-6xl mx-auto px-4 py-12">
      <div class="flex flex-col items-center gap-8 md:flex-row md:justify-between">
        <!-- 版权信息 -->
        <div class="text-center md:text-left">
          <div class="flex items-center justify-center gap-2 md:justify-start">
            <span class="flex h-7 w-7 items-center justify-center rounded-md bg-gradient-to-br from-indigo-500 to-violet-600 text-xs font-bold text-white shadow-glow">C</span>
            <p class="text-base font-extrabold tracking-tight text-slate-900 dark:text-white">
              code-assistant-live2d<span class="text-gradient"> 心流编程</span>
            </p>
          </div>
          <p class="mt-2 text-sm text-slate-500 dark:text-slate-400">
            © {{ year }} {{ profile.name }} · 基于 Vue 3 + Vite + TypeScript 构建
          </p>
        </div>

        <!-- 导航链接 -->
        <nav class="flex flex-wrap justify-center gap-x-6 gap-y-2">
          <RouterLink
            v-for="link in links"
            :key="link.name"
            :to="{ name: link.name }"
            class="text-sm font-medium text-slate-500 transition hover:text-indigo-600 dark:text-slate-400 dark:hover:text-indigo-400"
          >
            {{ link.label }}
          </RouterLink>
        </nav>

        <!-- 社交图标 -->
        <div class="flex gap-2.5">
          <a
            v-for="social in profile.socials"
            :key="social.platform"
            :href="social.url"
            target="_blank"
            rel="noopener"
            :aria-label="social.platform"
            :title="social.platform"
            class="flex h-9 w-9 items-center justify-center rounded-lg border border-slate-200 bg-white text-xs font-bold text-slate-600 transition hover:-translate-y-0.5 hover:border-indigo-400 hover:text-indigo-600 hover:shadow-soft dark:border-slate-700 dark:bg-slate-900 dark:text-slate-300 dark:hover:border-indigo-500 dark:hover:text-indigo-400"
          >
            {{ social.icon }}
          </a>
        </div>
      </div>
    </div>
  </footer>
</template>
