<script setup lang="ts">
import { computed, ref } from 'vue'
import { projects, subsystems } from '@/assets/data/projects'
import type { SubsystemKey } from '@/assets/data/projects'
import ProjectCard from '@/components/ProjectCard.vue'
import SectionTitle from '@/components/SectionTitle.vue'

const dynamicProjects = computed(() => projects.filter((p) => p.subsystem === 'dynamic'))
const immersiveProjects = computed(() => projects.filter((p) => p.subsystem === 'immersive'))

const allTags = computed(() => {
  const set = new Set<string>()
  projects.forEach((p) => p.tags.forEach((t) => set.add(t)))
  return ['全部', ...Array.from(set)]
})

const activeTag = ref<string>('全部')

const filteredDynamic = computed(() =>
  activeTag.value === '全部'
    ? dynamicProjects.value
    : dynamicProjects.value.filter((p) => p.tags.includes(activeTag.value)),
)

const filteredImmersive = computed(() =>
  activeTag.value === '全部'
    ? immersiveProjects.value
    : immersiveProjects.value.filter((p) => p.tags.includes(activeTag.value)),
)

function selectTag(tag: string): void {
  activeTag.value = tag
}

const subsystemEntries = Object.entries(subsystems) as [SubsystemKey, (typeof subsystems)[SubsystemKey]][]
</script>

<template>
  <div class="max-w-6xl mx-auto px-4 py-8">
    <SectionTitle
      eyebrow="MODULES"
      title="功能模块"
      subtitle="code-assistant-live2d 以心流理论为核心，通过动态难度调节与沉浸感优化两大子系统共 8 个模块，构建完整的「学—练—评—反馈」心流闭环。"
    />

    <!-- 标签筛选 -->
    <div class="mt-8 flex flex-wrap justify-center gap-2">
      <button
        v-for="tag in allTags"
        :key="tag"
        type="button"
        class="rounded-full border px-4 py-1.5 text-sm font-medium transition"
        :class="
          activeTag === tag
            ? 'border-indigo-600 bg-indigo-600 text-white shadow-glow'
            : 'border-slate-200 bg-white text-slate-600 hover:border-indigo-400 hover:text-indigo-600 dark:border-slate-700 dark:bg-slate-900 dark:text-slate-300'
        "
        @click="selectTag(tag)"
      >
        {{ tag }}
      </button>
    </div>

    <!-- 按子系统分组展示 -->
    <section
      v-for="([key, sub], idx) in subsystemEntries"
      :key="key"
      class="mt-14"
    >
      <div class="flex items-center gap-3 border-l-4 border-indigo-500 pl-4">
        <span class="flex h-11 w-11 items-center justify-center rounded-xl bg-gradient-to-br from-indigo-50 to-violet-50 text-lg font-bold text-indigo-600 dark:from-indigo-950 dark:to-violet-950 dark:text-indigo-400">{{ sub.icon }}</span>
        <div>
          <span class="text-xs font-semibold uppercase tracking-wider text-indigo-600 dark:text-indigo-400">Subsystem {{ idx + 1 }}</span>
          <h2 class="text-xl font-bold text-slate-900 dark:text-white">{{ sub.name }}</h2>
          <p class="text-sm text-slate-500 dark:text-slate-400">{{ sub.goal }}</p>
        </div>
      </div>

      <div class="mt-6 grid gap-6 sm:grid-cols-2">
        <ProjectCard
          v-for="project in (key === 'dynamic' ? filteredDynamic : filteredImmersive)"
          :key="project.id"
          :id="project.id"
          :title="`${project.moduleNo} ${project.title}`"
          :description="project.description"
          :tags="project.tags"
          :image-url="project.imageUrl"
        />
      </div>

      <p
        v-if="(key === 'dynamic' ? filteredDynamic : filteredImmersive).length === 0"
        class="mt-8 text-center text-slate-500 dark:text-slate-400"
      >
        该子系统暂无符合此标签的模块。
      </p>
    </section>
  </div>
</template>
