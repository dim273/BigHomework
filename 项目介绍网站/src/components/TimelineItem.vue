<script setup lang="ts">
interface Props {
  /** 日期 / 时间段 */
  date: string
  /** 条目标题 */
  title: string
  /** 条目描述 */
  description: string
  /** 在桌面端展示在哪一侧 */
  side: 'left' | 'right'
}

defineProps<Props>()
</script>

<template>
  <li class="relative animate-fade-up">
    <!-- 时间线圆点：渐变 + 光晕 -->
    <span
      class="absolute left-4 top-5 z-10 flex h-4 w-4 items-center justify-center rounded-full bg-gradient-to-br from-indigo-500 to-violet-600 shadow-glow ring-4 ring-white md:left-1/2 md:-translate-x-1/2 dark:ring-slate-950"
      aria-hidden="true"
    ></span>

    <div class="md:grid md:grid-cols-2 md:gap-x-12">
      <div
        class="ml-12 rounded-xl border border-slate-200/80 bg-white p-5 shadow-soft transition hover:-translate-y-0.5 hover:shadow-glow md:ml-0 dark:border-slate-800/80 dark:bg-slate-900"
        :class="side === 'left' ? 'md:col-start-1 md:text-right' : 'md:col-start-2'"
      >
        <span class="inline-block text-sm font-semibold text-indigo-600 dark:text-indigo-400">{{ date }}</span>
        <h4 class="mt-1 text-base font-semibold text-slate-900 dark:text-white">{{ title }}</h4>
        <p class="mt-2 text-sm leading-relaxed text-slate-600 dark:text-slate-300">{{ description }}</p>
      </div>
    </div>
  </li>
</template>
