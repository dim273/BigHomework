<script setup lang="ts">
interface Props {
  /** 标签名 */
  name: string
  /** 可选的主题色，建议传 hex 色值（如 #3178c6），会自动生成浅色背景 */
  color?: string
}

withDefaults(defineProps<Props>(), { color: '' })
</script>

<template>
  <span
    class="inline-flex items-center rounded-md px-2 py-0.5 text-xs font-medium transition"
    :class="!color && 'bg-slate-100/80 text-slate-600 dark:bg-slate-800/80 dark:text-slate-300'"
    :style="color ? { color, backgroundColor: `${color}1a` } : undefined"
  >
    {{ name }}
  </span>
</template>
