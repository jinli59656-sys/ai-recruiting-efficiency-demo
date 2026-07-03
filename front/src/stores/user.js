import { defineStore } from 'pinia'

const STORAGE_KEY = 'hr-assistant-user'

function loadUser() {
  try {
    const raw = localStorage.getItem(STORAGE_KEY)
    return raw ? JSON.parse(raw) : null
  } catch {
    return null
  }
}

export const useUserStore = defineStore('user', {
  state: () => ({
    userInfo: loadUser(),
  }),
  getters: {
    isLoggedIn: (state) => !!state.userInfo,
    displayName: (state) => state.userInfo?.username || '管理员',
  },
  actions: {
    setUser(user) {
      this.userInfo = user
      localStorage.setItem(STORAGE_KEY, JSON.stringify(user))
    },
    logout() {
      this.userInfo = null
      localStorage.removeItem(STORAGE_KEY)
    },
  },
})
