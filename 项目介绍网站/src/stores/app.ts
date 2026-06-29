import { defineStore } from 'pinia'
import { ref } from 'vue'

export const useAppStore = defineStore('app', () => {
  // 移动端导航菜单开关
  const isMenuOpen = ref(false)

  function toggleMenu(): void {
    isMenuOpen.value = !isMenuOpen.value
  }

  function closeMenu(): void {
    isMenuOpen.value = false
  }

  return { isMenuOpen, toggleMenu, closeMenu }
})
