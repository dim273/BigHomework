<script setup lang="ts">
import TechTag from '@/components/TechTag.vue'

interface Props {
  /** 项目 ID，用于跳转详情页 */
  id: number | string
  /** 项目标题 */
  title: string
  /** 项目描述 */
  description: string
  /** 技术标签数组 */
  tags: string[]
  /** 封面图地址（留空则显示渐变占位） */
  imageUrl?: string
  /** GitHub 仓库地址 */
  githubUrl?: string
  /** 在线 Demo 地址 */
  demoUrl?: string
}

withDefaults(defineProps<Props>(), {
  imageUrl: '',
  githubUrl: '',
  demoUrl: '',
})
</script>

<template>
  <article
    class="card-glow group relative flex flex-col overflow-hidden rounded-2xl border border-slate-200/80 bg-white shadow-soft transition duration-300 hover:-translate-y-1.5 hover:shadow-glow dark:border-slate-800/80 dark:bg-slate-900"
  >
    <!-- 封面图 / 渐变占位 -->
    <div class="relative h-36 overflow-hidden">
      <img
        v-if="imageUrl"
        :src="imageUrl"
        :alt="title"
        class="h-full w-full object-cover transition duration-500 group-hover:scale-105"
      />
      <div
        v-else
        class="relative flex h-full w-full items-center justify-center bg-gradient-to-br from-indigo-500 via-violet-500 to-fuchsia-500"
      >
        <!-- 装饰光斑 -->
        <div class="absolute -left-8 -top-8 h-24 w-24 rounded-full bg-white/20 blur-2xl"></div>
        <div class="absolute right-4 bottom-2 h-20 w-20 rounded-full bg-white/10 blur-xl"></div>
        <span class="text-2xl font-bold text-white/90 drop-shadow-sm">{{ title }}</span>
      </div>
    </div>

    <!-- 内容区 -->
    <div class="flex flex-1 flex-col p-5">
      <h3 class="text-base font-semibold text-slate-900 dark:text-white">{{ title }}</h3>
      <p class="mt-2 flex-1 text-sm leading-relaxed text-slate-600 dark:text-slate-300">{{ description }}</p>

      <!-- 技术标签 -->
      <div class="mt-4 flex flex-wrap gap-1.5">
        <TechTag v-for="tag in tags" :key="tag" :name="tag" />
      </div>

      <!-- 外部链接 -->
      <div
        v-if="githubUrl || demoUrl"
        class="relative z-10 mt-4 flex gap-4 border-t border-slate-100 pt-3 dark:border-slate-800"
      >
        <a
          v-if="githubUrl"
          :href="githubUrl"
          target="_blank"
          rel="noopener"
          class="text-sm font-medium text-slate-500 transition hover:text-indigo-600 dark:text-slate-400 dark:hover:text-indigo-400"
        >
          GitHub ↗
        </a>
        <a
          v-if="demoUrl"
          :href="demoUrl"
          target="_blank"
          rel="noopener"
          class="text-sm font-medium text-slate-500 transition hover:text-indigo-600 dark:text-slate-400 dark:hover:text-indigo-400"
        >
          在线 Demo ↗
        </a>
      </div>

      <span class="mt-4 inline-flex items-center gap-1 text-sm font-semibold text-indigo-600 dark:text-indigo-400">
        查看详情
        <span class="transition-transform duration-300 group-hover:translate-x-1">→</span>
      </span>
    </div>

    <!-- 拉伸链接：覆盖整张卡片以触发跳转，避免 <a> 嵌套 -->
    <RouterLink
      :to="{ name: 'project-detail', params: { id } }"
      class="after:absolute after:inset-0"
      :aria-label="`查看「${title}」详情`"
    />
  </article>
</template>
