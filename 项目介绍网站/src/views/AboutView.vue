<script setup lang="ts">
import { profile } from '@/assets/data/profile'
import SectionTitle from '@/components/SectionTitle.vue'
import TimelineItem from '@/components/TimelineItem.vue'
import logoImg from '@/assets/pic/logo.png'

const innovations = [
  {
    icon: '01',
    title: '心流理论驱动的系统设计框架',
    desc: '创新性地将心流理论引入编程学习支持系统，通过动态难度调节子系统提高心流触发概率，依托沉浸感优化子系统延长心流停留时间，两大子系统相辅相成构建心流闭环。',
  },
  {
    icon: '02',
    title: '知识图谱 + 闯关式学习路径',
    desc: '将编程知识体系按先修后继关系整理为知识图谱中的知识节点，并引入闯关式设计。这种设计将抽象、长期的学习目标拆分为具体、即时、可达成的小目标，通过先修后继关系确保认知水平始终与挑战难度匹配。',
  },
  {
    icon: '03',
    title: '大模型从「答案提供者」到「学习辅助者」',
    desc: '大模型不再直接为学习者提供题目代码，而是根据学习者能力水平帮助进行问题分解与引导，让学习者逐步自主编写完整代码。一方面减少对大模型的过度依赖，另一方面通过引导而非提供答案增强成就感与获得感。',
  },
  {
    icon: '04',
    title: '认知-情感协同萌伴',
    desc: '引入萌伴系统，通过与学习者的行为交互，解决传统教育工具中认知训练与情感激励割裂的痛点，维持学习者的学习热情与内在动机。',
  },
]
</script>

<template>
  <div class="max-w-6xl mx-auto px-4 py-8">
    <SectionTitle eyebrow="ABOUT" title="关于项目" />

    <!-- 项目简介 -->
    <section
      class="mt-8 relative overflow-hidden rounded-2xl border border-slate-200/80 bg-white p-8 shadow-soft dark:border-slate-800/80 dark:bg-slate-900"
    >
      <div class="pointer-events-none absolute -right-12 -top-12 h-40 w-40 rounded-full bg-gradient-to-br from-indigo-100 to-violet-100 opacity-60 dark:from-indigo-950 dark:to-violet-950"></div>
      <div class="relative flex flex-col items-center gap-6 md:flex-row md:items-start">
        <div
          class="flex h-24 w-24 shrink-0 items-center justify-center overflow-hidden rounded-2xl bg-gradient-to-br from-indigo-500 to-violet-600 shadow-glow"
        >
          <img :src="logoImg" alt="logo" class="h-full w-full object-cover" />
        </div>
        <div class="text-center md:text-left">
          <h2 class="text-2xl font-extrabold tracking-tight text-slate-900 dark:text-white">{{ profile.name }}</h2>
          <p class="mt-1 text-sm font-semibold text-indigo-600 dark:text-indigo-400">{{ profile.title }}</p>
          <p class="mt-1 text-sm text-slate-500 dark:text-slate-400">
            {{ profile.affiliation }} · {{ profile.location }}
          </p>
          <p class="mt-4 leading-relaxed text-slate-600 dark:text-slate-300">{{ profile.bio }}</p>
        </div>
      </div>
    </section>

    <!-- 研究背景与意义 -->
    <section class="mt-12">
      <h3 class="text-lg font-bold text-slate-900 dark:text-white">
        研究背景与意义
      </h3>
      <div class="mt-4 grid gap-5 md:grid-cols-2">
        <div class="rounded-2xl border border-slate-200/80 bg-slate-50/60 p-6 dark:border-slate-800/80 dark:bg-slate-900/60">
          <h4 class="font-semibold text-indigo-600 dark:text-indigo-400">心流理论</h4>
          <p class="mt-2 text-sm leading-relaxed text-slate-600 dark:text-slate-300">
            心流理论由米哈里·契克森米哈伊于 20 世纪 70 年代提出：当任务难度与个体能力动态匹配时，人会进入「心流区」，表现出时间感扭曲、自我意识消失、沉浸式投入的行为，并获得强烈的内在满足感。DuoLingo（留存率 93%）、可汗学院（中等以下学生比例 13%→3%）等案例验证了其在教育场景中的有效性。
          </p>
        </div>
        <div class="rounded-2xl border border-slate-200/80 bg-slate-50/60 p-6 dark:border-slate-800/80 dark:bg-slate-900/60">
          <h4 class="font-semibold text-rose-600 dark:text-rose-400">编程学习痛点</h4>
          <p class="mt-2 text-sm leading-relaxed text-slate-600 dark:text-slate-300">
            编程学习具有高认知负荷、强逻辑性与实践性特征，初学者常因缺乏适度难度引导和及时反馈陷入认知超载。大语言模型虽便利，却让学习者放弃自主思考、基础技能退化，内在动机评分较对照组下降 22%。目前编程学习领域尚未形成以心流理论为核心的系统设计框架。
          </p>
        </div>
      </div>
    </section>

    <!-- 创新点 -->
    <section class="mt-12">
      <h3 class="text-lg font-bold text-slate-900 dark:text-white">
        项目特色与创新点
      </h3>
      <div class="mt-4 grid gap-5 md:grid-cols-2">
        <div
          v-for="inn in innovations"
          :key="inn.title"
          class="card-glow group rounded-2xl border border-slate-200/80 bg-white p-6 shadow-soft transition hover:-translate-y-1 hover:shadow-glow dark:border-slate-800/80 dark:bg-slate-900"
        >
          <div class="flex h-11 w-11 items-center justify-center rounded-xl bg-gradient-to-br from-indigo-50 to-violet-50 text-sm font-bold text-indigo-600 transition group-hover:scale-110 dark:from-indigo-950 dark:to-violet-950 dark:text-indigo-400">{{ inn.icon }}</div>
          <h4 class="mt-4 font-semibold text-slate-900 dark:text-white">{{ inn.title }}</h4>
          <p class="mt-2 text-sm leading-relaxed text-slate-600 dark:text-slate-300">{{ inn.desc }}</p>
        </div>
      </div>
    </section>

    <!-- 技术栈 -->
    <section class="mt-12">
      <h3 class="text-lg font-bold text-slate-900 dark:text-white">
        技术栈
      </h3>
      <div class="mt-4 flex flex-wrap gap-2">
        <span
          v-for="skill in profile.skills"
          :key="skill"
          class="rounded-lg border border-indigo-200/70 bg-indigo-50/60 px-3 py-1.5 text-sm font-medium text-indigo-700 transition hover:-translate-y-0.5 hover:bg-indigo-100 dark:border-indigo-900/70 dark:bg-indigo-950/40 dark:text-indigo-300 dark:hover:bg-indigo-950"
        >
          {{ skill }}
        </span>
      </div>
    </section>

    <!-- 开发历程时间线 -->
    <section class="mt-16">
      <SectionTitle eyebrow="PROGRESS" title="研究进展" subtitle="code-assistant-live2d 项目的研究计划执行情况与主要进展" />
      <ol
        class="relative mt-10 space-y-8 before:absolute before:top-0 before:bottom-0 before:left-6 before:w-0.5 before:bg-gradient-to-b before:from-indigo-200 before:to-violet-200 md:before:left-1/2 md:before:-translate-x-1/2 dark:before:from-indigo-900 dark:before:to-violet-900"
      >
        <TimelineItem
          v-for="(exp, index) in profile.experiences"
          :key="exp.period"
          :date="exp.period"
          :title="exp.title"
          :description="`${exp.org} · ${exp.description}`"
          :side="index % 2 === 0 ? 'left' : 'right'"
        />
      </ol>
    </section>

    <!-- 社交账号 -->
    <section class="mt-16">
      <SectionTitle eyebrow="LINKS" title="相关链接" subtitle="欢迎通过以下方式获取 code-assistant-live2d 源码、安装插件或反馈问题。" />
      <div class="mt-8 grid gap-5 sm:grid-cols-2 lg:grid-cols-4">
        <a
          v-for="social in profile.socials"
          :key="social.platform"
          :href="social.url"
          target="_blank"
          rel="noopener"
          class="card-glow group rounded-2xl border border-slate-200/80 bg-white p-6 shadow-soft transition hover:-translate-y-1.5 hover:shadow-glow dark:border-slate-800/80 dark:bg-slate-900"
        >
          <div class="flex h-11 w-11 items-center justify-center rounded-xl bg-gradient-to-br from-indigo-50 to-violet-50 text-xs font-bold text-indigo-600 transition group-hover:scale-110 dark:from-indigo-950 dark:to-violet-950 dark:text-indigo-400">{{ social.icon }}</div>
          <h3 class="mt-3 font-semibold text-slate-900 dark:text-white">{{ social.platform }}</h3>
          <p class="mt-1 text-sm text-slate-500 dark:text-slate-400">{{ social.desc }}</p>
          <span class="mt-3 inline-flex items-center gap-1 text-sm font-medium text-indigo-600 transition dark:text-indigo-400">
            访问
            <span class="transition-transform duration-300 group-hover:translate-x-0.5">↗</span>
          </span>
        </a>
      </div>
    </section>

    <!-- 项目信息 -->
    <section
      class="mt-10 grid gap-6 rounded-2xl border border-slate-200/80 bg-slate-50/60 p-8 sm:grid-cols-2 dark:border-slate-800/80 dark:bg-slate-900/60"
    >
      <div>
        <h3 class="text-xs font-semibold uppercase tracking-wider text-slate-500 dark:text-slate-400">所在地区</h3>
        <p class="mt-1.5 text-lg font-semibold text-slate-900 dark:text-white">{{ profile.location }}</p>
      </div>
      <div>
        <h3 class="text-xs font-semibold uppercase tracking-wider text-slate-500 dark:text-slate-400">项目性质</h3>
        <p class="mt-1.5 text-lg font-semibold text-slate-900 dark:text-white">{{ profile.affiliation }}</p>
      </div>
    </section>
  </div>
</template>
