<script setup lang="ts">
import { projects, subsystems } from '@/assets/data/projects'
import { profile } from '@/assets/data/profile'
import ProjectCard from '@/components/ProjectCard.vue'
import SectionTitle from '@/components/SectionTitle.vue'
import mainInterfaceImg from '@/assets/pic/主界面.png'

// 每个子系统取前 2 个模块作为首页预览
const dynamicPreview = projects.filter((p) => p.subsystem === 'dynamic').slice(0, 2)
const immersivePreview = projects.filter((p) => p.subsystem === 'immersive').slice(0, 2)

const stats = [
  { label: '子系统', value: '2' },
  { label: '功能模块', value: String(projects.length) },
  { label: '核心技术', value: String(profile.skills.length) },
]

// 问题与挑战数据
const challenges = [
  {
    icon: '01',
    title: '编程学习认知超载',
    desc: '编程学习具有高认知负荷、强逻辑性与实践性特征，初学者常因缺乏适度难度引导和及时反馈，陷入「认知超载」或「效率低下」状态，最终导致学习动机下降。',
  },
  {
    icon: '02',
    title: '大模型依赖陷阱',
    desc: '大语言模型能直接提供代码，学习者会放弃自主思考转而索取答案，导致基础技能退化。研究显示，使用 Copilot 的学生在独立编程时焦虑程度更高，内在动机评分较对照组下降 22%。',
  },
  {
    icon: '03',
    title: '胜任感异化',
    desc: '当大模型替代了代码调试、算法设计等过程，学习者难以获得突破困难后的成就感，胜任感来源从「我能解决问题」异化为「工具能解决问题」，削弱内在驱动。',
  },
]

// 心流理论教育应用案例
const cases = [
  { name: 'DuoLingo', metric: '93%', desc: '通过游戏化设计与即时反馈，用户平均留存率提升至 93%' },
  { name: '可汗学院', metric: '13%→3%', desc: '引入心流理论重构学习路径后，期末中等以下学生比例从 13% 降至 3%' },
]
</script>

<template>
  <div class="max-w-6xl mx-auto px-4 py-8">
    <!-- Hero 首屏 -->
    <section class="relative overflow-hidden py-16 text-center md:py-24">
      <!-- 网格背景 + 光斑装饰 -->
      <div class="pointer-events-none absolute inset-0 bg-grid bg-grid-fade"></div>
      <div class="pointer-events-none absolute -top-20 left-1/4 h-72 w-72 rounded-full bg-indigo-400/20 blur-3xl animate-float-slow"></div>
      <div class="pointer-events-none absolute -top-10 right-1/4 h-64 w-64 rounded-full bg-violet-400/20 blur-3xl animate-float-slower"></div>

      <div class="relative">
        <span
          class="inline-flex items-center gap-1.5 rounded-full border border-indigo-200 bg-indigo-50/80 px-3.5 py-1 text-sm font-medium text-indigo-600 backdrop-blur-sm dark:border-indigo-900 dark:bg-indigo-950/40 dark:text-indigo-300 animate-fade-up"
        >
          <span class="flex h-1.5 w-1.5 rounded-full bg-indigo-500 animate-pulse"></span>
          心流理论 · 编程学习支持系统
        </span>
        <h1 class="mt-6 text-4xl font-extrabold tracking-tight text-slate-900 md:text-6xl dark:text-white animate-fade-up" style="--ad: 0.05s">
          code-assistant-live2d <span class="text-gradient">心流编程</span>
        </h1>
        <p class="mx-auto mt-6 max-w-2xl text-lg leading-relaxed text-slate-600 dark:text-slate-300 animate-fade-up" style="--ad: 0.1s">
          以心流理论为核心指导，通过动态难度调节子系统维持挑战与能力的平衡，依托沉浸感优化子系统营造无干扰专注环境，将高认知负荷的编程学习转换为目标清晰、反馈及时的「心流旅程」。
        </p>
        <div class="mt-8 flex flex-wrap items-center justify-center gap-3 animate-fade-up" style="--ad: 0.15s">
          <RouterLink
            to="/projects"
            class="group inline-flex items-center gap-1.5 rounded-xl bg-gradient-to-r from-indigo-600 to-violet-600 px-6 py-3 text-sm font-semibold text-white shadow-glow transition hover:shadow-lg hover:brightness-110"
          >
            查看功能模块
            <span class="transition-transform duration-300 group-hover:translate-x-0.5">→</span>
          </RouterLink>
          <RouterLink
            to="/about"
            class="rounded-xl border border-slate-200 bg-white/80 px-6 py-3 text-sm font-semibold text-slate-700 backdrop-blur-sm transition hover:bg-slate-50 hover:shadow-soft dark:border-slate-700 dark:bg-slate-900/80 dark:text-slate-200 dark:hover:bg-slate-800"
          >
            研究背景
          </RouterLink>
        </div>
      </div>
    </section>

    <!-- 数据统计 -->
    <section class="grid grid-cols-1 gap-4 rounded-2xl border border-slate-200/80 bg-white/60 p-6 shadow-soft backdrop-blur-sm sm:grid-cols-3 dark:border-slate-800/80 dark:bg-slate-900/60 animate-fade-up" style="--ad: 0.2s">
      <div v-for="stat in stats" :key="stat.label" class="text-center">
        <div class="text-3xl font-extrabold text-gradient">{{ stat.value }}</div>
        <div class="mt-1 text-sm text-slate-500 dark:text-slate-400">{{ stat.label }}</div>
      </div>
    </section>

    <!-- 心流理论简介 -->
    <section class="mt-12 overflow-hidden rounded-2xl border border-indigo-200/60 bg-gradient-to-br from-indigo-50/80 to-violet-50/80 p-8 shadow-soft dark:border-indigo-900/60 dark:from-indigo-950/30 dark:to-violet-950/30">
      <div class="flex flex-col items-start gap-6 md:flex-row md:items-center">
        <div class="flex-1">
          <h2 class="text-xl font-bold text-slate-900 dark:text-white">心流理论（Flow Theory）</h2>
          <p class="mt-2 leading-relaxed text-slate-600 dark:text-slate-300">
            心流理论由心理学家米哈里·契克森米哈伊于 20 世纪 70 年代提出：当任务难度与个体能力动态匹配时，人会进入「心流区」，表现出时间感扭曲、自我意识消失、沉浸式投入的行为，并获得强烈的内在满足感。本系统将这一理论系统性地应用于编程学习场景。
          </p>
          <div class="mt-4 grid gap-4 sm:grid-cols-2">
            <div v-for="c in cases" :key="c.name" class="rounded-xl border border-white/60 bg-white/70 p-4 backdrop-blur-sm dark:border-slate-700/60 dark:bg-slate-900/70">
              <div class="flex items-baseline gap-2">
                <span class="text-lg font-bold text-indigo-600 dark:text-indigo-400">{{ c.name }}</span>
                <span class="text-2xl font-extrabold text-slate-900 dark:text-white">{{ c.metric }}</span>
              </div>
              <p class="mt-1 text-sm text-slate-500 dark:text-slate-400">{{ c.desc }}</p>
            </div>
          </div>
        </div>
      </div>
    </section>

    <!-- 问题与挑战 -->
    <section class="mt-16">
      <SectionTitle eyebrow="PAIN POINTS" title="问题与挑战" subtitle="编程学习面临的三大核心痛点" />
      <div class="mt-8 grid gap-5 md:grid-cols-3">
        <div
          v-for="(ch, i) in challenges"
          :key="ch.title"
          class="card-glow group rounded-2xl border border-slate-200/80 bg-white p-6 shadow-soft transition hover:-translate-y-1 hover:shadow-glow dark:border-slate-800/80 dark:bg-slate-900 animate-fade-up"
          :style="`--ad: ${i * 0.08}s`"
        >
          <div class="flex h-11 w-11 items-center justify-center rounded-xl bg-slate-50 text-sm font-bold text-indigo-600 transition group-hover:scale-110 dark:bg-slate-800 dark:text-indigo-400">{{ ch.icon }}</div>
          <h3 class="mt-4 font-semibold text-slate-900 dark:text-white">{{ ch.title }}</h3>
          <p class="mt-2 text-sm leading-relaxed text-slate-600 dark:text-slate-300">{{ ch.desc }}</p>
        </div>
      </div>
    </section>

    <!-- 两大子系统 -->
    <section class="mt-16">
      <SectionTitle eyebrow="SOLUTION" title="解决方案" subtitle="两大子系统相辅相成，共同构建心流闭环" />
      <div class="mt-8 grid gap-6 md:grid-cols-2">
        <div
          v-for="(sub, key) in subsystems"
          :key="key"
          class="group relative overflow-hidden rounded-2xl border border-slate-200/80 bg-white p-8 shadow-soft transition hover:-translate-y-1 hover:shadow-glow dark:border-slate-800/80 dark:bg-slate-900"
        >
          <div class="absolute -right-8 -top-8 h-32 w-32 rounded-full bg-gradient-to-br from-indigo-100 to-violet-100 opacity-0 transition group-hover:opacity-100 dark:from-indigo-950 dark:to-violet-950"></div>
          <div class="relative">
            <div class="flex items-center gap-3">
              <span class="flex h-12 w-12 items-center justify-center rounded-xl bg-gradient-to-br from-indigo-50 to-violet-50 text-lg font-bold text-indigo-600 dark:from-indigo-950 dark:to-violet-950 dark:text-indigo-400">{{ sub.icon }}</span>
              <h3 class="text-lg font-bold text-slate-900 dark:text-white">{{ sub.name }}</h3>
            </div>
            <p class="mt-3 text-sm leading-relaxed text-slate-600 dark:text-slate-300">{{ sub.goal }}</p>
            <div class="mt-5 flex flex-wrap gap-2">
              <span
                v-for="p in projects.filter((item) => item.subsystem === key)"
                :key="p.id"
                class="rounded-md bg-slate-100/80 px-2.5 py-1 text-xs font-medium text-slate-600 dark:bg-slate-800/80 dark:text-slate-300"
              >
                {{ p.moduleNo }} {{ p.title }}
              </span>
            </div>
          </div>
        </div>
      </div>
    </section>

    <!-- 系统预览 -->
    <section class="mt-16">
      <SectionTitle eyebrow="PREVIEW" title="系统预览" subtitle="单 Webview 多页面 SPA 架构，整合学习、练习、评测与反馈的沉浸式编程环境" />
      <figure class="mt-8 overflow-hidden rounded-2xl border border-slate-200/80 bg-white shadow-soft dark:border-slate-800/80 dark:bg-slate-900">
        <div class="overflow-hidden">
          <img
            :src="mainInterfaceImg"
            alt="code-assistant-live2d 主界面"
            class="w-full object-cover transition duration-500 hover:scale-[1.02]"
          />
        </div>
        <figcaption class="border-t border-slate-100 px-6 py-4 text-sm text-slate-500 dark:border-slate-800 dark:text-slate-400">
          主界面：通过内部状态机切换 10+ 页面，整合登录、知识树、题单、题目作答、AI 助教与能力画像等功能，减少注意力碎片化。
        </figcaption>
      </figure>
    </section>

    <!-- 动态难度调节子系统 模块预览 -->
    <section class="mt-16">
      <SectionTitle :eyebrow="`SUBSYSTEM 1`" :title="subsystems.dynamic.name" :subtitle="subsystems.dynamic.goal" />
      <div class="mt-8 grid gap-6 md:grid-cols-2">
        <ProjectCard
          v-for="project in dynamicPreview"
          :key="project.id"
          :id="project.id"
          :title="`${project.moduleNo} ${project.title}`"
          :description="project.description"
          :tags="project.tags"
          :image-url="project.imageUrl"
        />
      </div>
    </section>

    <!-- 沉浸感优化子系统 模块预览 -->
    <section class="mt-16">
      <SectionTitle :eyebrow="`SUBSYSTEM 2`" :title="subsystems.immersive.name" :subtitle="subsystems.immersive.goal" />
      <div class="mt-8 grid gap-6 md:grid-cols-2">
        <ProjectCard
          v-for="project in immersivePreview"
          :key="project.id"
          :id="project.id"
          :title="`${project.moduleNo} ${project.title}`"
          :description="project.description"
          :tags="project.tags"
          :image-url="project.imageUrl"
        />
      </div>
      <div class="mt-8 text-center">
        <RouterLink
          to="/projects"
          class="group inline-flex items-center gap-1 text-sm font-semibold text-indigo-600 hover:underline dark:text-indigo-400"
        >
          查看全部 8 个模块
          <span class="transition-transform duration-300 group-hover:translate-x-0.5">→</span>
        </RouterLink>
      </div>
    </section>
  </div>
</template>
