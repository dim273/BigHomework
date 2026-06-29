import { useDark, useToggle } from '@vueuse/core'

/**
 * 暗色模式组合式函数
 * 基于 @vueuse/core 的 useDark，自动在 <html> 上切换 .dark 类并持久化到 localStorage
 */
export function useTheme() {
  const isDark = useDark()
  const toggleDark = useToggle(isDark)

  return { isDark, toggleDark }
}
