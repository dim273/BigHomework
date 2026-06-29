<script setup lang="ts">
import { computed } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { projects, subsystems } from '@/assets/data/projects'
import type { Project } from '@/assets/data/projects'

const route = useRoute()
const router = useRouter()

const project = computed<Project | undefined>(() =>
  projects.find((p) => p.id === Number(route.params.id)),
)

function goBack(): void {
  router.push({ name: 'projects' })
}
</script>

<template>
  <div class="max-w-6xl mx-auto px-4 py-8">
    <template v-if="project">
      <!-- 返回按钮 -->
      <button
        type="button"
        class="group mb-6 inline-flex items-center gap-1.5 text-sm font-medium text-slate-600 transition hover:text-indigo-600 dark:text-slate-300 dark:hover:text-indigo-400"
        @click="goBack"
      >
        <span class="transition-transform duration-300 group-hover:-translate-x-0.5">←</span>
        返回功能模块
      </button>

      <!-- 标题区 -->
      <header class="relative overflow-hidden rounded-2xl border border-slate-200/80 bg-white p-8 shadow-soft dark:border-slate-800/80 dark:bg-slate-900">
        <div class="pointer-events-none absolute -right-12 -top-12 h-40 w-40 rounded-full bg-gradient-to-br from-indigo-100 to-violet-100 opacity-60 dark:from-indigo-950 dark:to-violet-950"></div>
        <div class="relative">
          <div class="flex flex-wrap items-center gap-2.5 text-sm">
            <span class="inline-flex items-center gap-1.5 rounded-full bg-indigo-50 px-3 py-1 font-medium text-indigo-600 dark:bg-indigo-950/60 dark:text-indigo-300">
              {{ subsystems[project.subsystem].icon }} {{ subsystems[project.subsystem].name }}
            </span>
            <span class="rounded-full bg-slate-100 px-3 py-1 font-mono text-slate-600 dark:bg-slate-800 dark:text-slate-300">
              模块 {{ project.moduleNo }}
            </span>
            <span class="inline-flex items-center gap-1.5 rounded-full bg-emerald-50 px-3 py-1 text-emerald-600 dark:bg-emerald-950/60 dark:text-emerald-300">
              <span class="flex h-1.5 w-1.5 rounded-full bg-emerald-500"></span>
              {{ project.status }}
            </span>
            <span class="text-slate-500 dark:text-slate-400">角色：{{ project.role }}</span>
          </div>
          <h1 class="mt-4 text-3xl font-extrabold tracking-tight text-slate-900 md:text-4xl dark:text-white">
            {{ project.title }}
          </h1>
          <p class="mt-3 max-w-3xl text-lg leading-relaxed text-slate-600 dark:text-slate-300">
            {{ project.description }}
          </p>
        </div>
      </header>

      <!-- 详细内容 -->
      <div class="mt-8 grid gap-8 lg:grid-cols-3">
        <!-- 左侧：效果截图 + 技术解析 + 技术亮点 -->
        <div class="space-y-8 lg:col-span-2">
          <figure v-if="project.imageUrl" class="overflow-hidden rounded-2xl border border-slate-200/80 bg-white shadow-soft dark:border-slate-800/80 dark:bg-slate-900">
            <div class="overflow-hidden">
              <img
                :src="project.imageUrl"
                :alt="`${project.title} 效果截图`"
                class="w-full object-cover transition duration-500 hover:scale-[1.02]"
              />
            </div>
            <figcaption class="border-t border-slate-100 px-6 py-3 text-sm text-slate-500 dark:border-slate-800 dark:text-slate-400">
              {{ project.title }} 效果截图
            </figcaption>
          </figure>

          <section class="rounded-2xl border border-slate-200/80 bg-white p-6 shadow-soft dark:border-slate-800/80 dark:bg-slate-900">
            <h2 class="text-lg font-bold text-slate-900 dark:text-white">
              技术解析
            </h2>
            <p class="mt-4 leading-relaxed text-slate-600 dark:text-slate-300">
              {{ project.detailedDescription }}
            </p>
          </section>

          <section class="rounded-2xl border border-slate-200/80 bg-white p-6 shadow-soft dark:border-slate-800/80 dark:bg-slate-900">
            <h2 class="text-lg font-bold text-slate-900 dark:text-white">
              技术亮点
            </h2>
            <ul class="mt-4 space-y-3">
              <li
                v-for="(highlight, idx) in project.highlights"
                :key="idx"
                class="flex items-start gap-3 text-slate-600 dark:text-slate-300"
              >
                <span class="mt-0.5 flex h-5 w-5 shrink-0 items-center justify-center rounded-full bg-gradient-to-br from-indigo-500 to-violet-600 text-xs text-white">
                  ✓
                </span>
                <span class="leading-relaxed">{{ highlight }}</span>
              </li>
            </ul>
          </section>
        </div>

        <!-- 右侧：子系统目标 + 技术栈 + 外链 -->
        <aside class="space-y-6">
          <div class="relative overflow-hidden rounded-2xl border border-indigo-200/60 bg-gradient-to-br from-indigo-50/80 to-violet-50/80 p-6 shadow-soft dark:border-indigo-900/60 dark:from-indigo-950/40 dark:to-violet-950/40">
            <h3 class="text-sm font-semibold uppercase tracking-wider text-indigo-600 dark:text-indigo-400">所属子系统目标</h3>
            <p class="mt-2 text-sm leading-relaxed text-indigo-700 dark:text-indigo-300">
              {{ subsystems[project.subsystem].goal }}
            </p>
          </div>

          <div class="rounded-2xl border border-slate-200/80 bg-white p-6 shadow-soft dark:border-slate-800/80 dark:bg-slate-900">
            <h3 class="font-semibold text-slate-900 dark:text-white">技术栈</h3>
            <div class="mt-3 flex flex-wrap gap-2">
              <span
                v-for="tech in project.techStack"
                :key="tech"
                class="rounded-md bg-slate-100/80 px-2.5 py-1 text-xs font-medium text-slate-600 dark:bg-slate-800/80 dark:text-slate-300"
              >
                {{ tech }}
              </span>
            </div>
          </div>

          <div class="rounded-2xl border border-slate-200/80 bg-white p-6 shadow-soft dark:border-slate-800/80 dark:bg-slate-900">
            <h3 class="font-semibold text-slate-900 dark:text-white">相关链接</h3>
            <a
              :href="project.link"
              target="_blank"
              rel="noopener"
              class="mt-3 inline-flex items-center gap-1 text-sm font-medium text-indigo-600 transition hover:gap-2 hover:text-indigo-700 dark:text-indigo-400"
            >
              查看源码 ↗
            </a>
          </div>
        </aside>
      </div>
    </template>

    <!-- 404 -->
    <template v-else>
      <div class="py-24 text-center">
        <p class="text-6xl font-extrabold text-slate-300 dark:text-slate-700">404</p>
        <h1 class="mt-4 text-2xl font-bold text-slate-900 dark:text-white">功能模块不存在</h1>
        <p class="mt-2 text-slate-500 dark:text-slate-400">未找到 ID 为 {{ route.params.id }} 的功能模块。</p>
        <RouterLink
          to="/projects"
          class="mt-6 inline-block rounded-xl bg-gradient-to-r from-indigo-600 to-violet-600 px-6 py-3 text-sm font-semibold text-white shadow-glow transition hover:brightness-110"
        >
          返回功能模块
        </RouterLink>
      </div>
    </template>
  </div>
</template>
