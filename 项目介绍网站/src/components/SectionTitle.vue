<script setup lang="ts">
interface Props {
  /** 区块标题 */
  title: string
  /** 可选副标题 */
  subtitle?: string
  /** 可选上方小标签 */
  eyebrow?: string
}

withDefaults(defineProps<Props>(), { subtitle: '', eyebrow: '' })
</script>

<template>
  <div class="text-center">
    <span
      v-if="eyebrow"
      class="inline-block rounded-full border border-indigo-200 bg-indigo-50/60 px-3 py-1 text-xs font-semibold uppercase tracking-wider text-indigo-600 dark:border-indigo-900 dark:bg-indigo-950/40 dark:text-indigo-400"
    >
      {{ eyebrow }}
    </span>
    <h2 class="mt-3 text-2xl font-bold tracking-tight text-slate-900 md:text-3xl dark:text-white">
      {{ title }}
    </h2>
    <p v-if="subtitle" class="mx-auto mt-3 max-w-2xl text-base leading-relaxed text-slate-600 dark:text-slate-300">
      {{ subtitle }}
    </p>
    <!-- 底部装饰线 -->
    <span class="mx-auto mt-4 block h-1 w-12 rounded-full bg-gradient-to-r from-indigo-500 to-violet-500"></span>
  </div>
</template>
