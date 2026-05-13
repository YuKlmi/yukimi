import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import { login as loginApi, changePassword as changePasswordApi } from '../api/auth'

export const useUserStore = defineStore('user', () => {
  const token = ref(localStorage.getItem('token') || '')
  const user = ref(JSON.parse(localStorage.getItem('user') || 'null'))

  const isLoggedIn = computed(() => !!token.value)
  const username = computed(() => user.value?.name || user.value?.username || '')
  const studentId = computed(() => user.value?.id || '')

  function saveUser(loginResponse) {
    token.value = 'logged_in'
    user.value = loginResponse
    localStorage.setItem('token', 'logged_in')
    localStorage.setItem('user', JSON.stringify(loginResponse))
  }

  async function login(credentials) {
    const res = await loginApi(credentials)
    saveUser(res.data || res)
    return res
  }

  function logout() {
    token.value = ''
    user.value = null
    localStorage.removeItem('token')
    localStorage.removeItem('user')
  }

  async function changePassword(oldPassword, newPassword) {
    const res = await changePasswordApi({
      username: user.value?.username || '',
      old_password: oldPassword,
      new_password: newPassword
    })
    return res
  }

  return {
    token,
    user,
    isLoggedIn,
    username,
    studentId,
    login,
    logout,
    changePassword
  }
})
