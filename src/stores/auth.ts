import { computed, ref } from 'vue'
import { defineStore } from 'pinia'
import { api, apiError } from '@/api/client'
import type { SessionUser, UserRole } from '@/types'

const AUTH_KEY = 'somnia-auth'
const TOKEN_KEY = 'somnia-token'

function loadSession(): SessionUser | null {
  const raw = localStorage.getItem(AUTH_KEY)
  if (!raw) return null
  try {
    return JSON.parse(raw) as SessionUser
  } catch {
    return null
  }
}

export const useAuthStore = defineStore('auth', () => {
  const user = ref<SessionUser | null>(loadSession())

  const isLoggedIn = computed(() => Boolean(user.value && localStorage.getItem(TOKEN_KEY)))
  const role = computed(() => user.value?.role ?? null)
  const isOwner = computed(() => Boolean(user.value?.isOwner))

  function persistSession() {
    if (user.value) localStorage.setItem(AUTH_KEY, JSON.stringify(user.value))
    else localStorage.removeItem(AUTH_KEY)
  }

  function acceptSession(data: SessionUser & { token: string }) {
    localStorage.setItem(TOKEN_KEY, data.token)
    user.value = {
      email: data.email,
      role: data.role,
      nickname: data.nickname,
      isOwner: data.isOwner,
      status: data.status,
    }
    persistSession()
  }

  async function login(email: string, password: string): Promise<string | null> {
    try {
      const { data } = await api.post('/auth/login', { email, password })
      acceptSession(data)
      return null
    } catch (error) {
      return apiError(error, '邮箱或密码不正确')
    }
  }

  async function register(
    email: string,
    password: string,
    nickname: string,
    role: UserRole,
  ): Promise<'pending' | string | null> {
    try {
      const { data } = await api.post('/auth/register', { email, password, nickname, role })
      if (data.pending) return 'pending'
      acceptSession(data)
      return null
    } catch (error) {
      return apiError(error, '注册失败')
    }
  }

  async function refreshProfile() {
    try {
      const { data } = await api.get<SessionUser>('/auth/me')
      if (user.value) {
        user.value = { ...user.value, ...data }
        persistSession()
      }
    } catch {
      /* 保持本地会话 */
    }
  }

  async function logout() {
    try {
      await api.post('/auth/logout')
    } catch {
      /* 本地清会话即可 */
    }
    user.value = null
    localStorage.removeItem(TOKEN_KEY)
    persistSession()
  }

  return { user, isLoggedIn, role, isOwner, login, register, refreshProfile, logout }
})
