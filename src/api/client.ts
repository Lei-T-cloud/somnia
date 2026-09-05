import axios from 'axios'

export const api = axios.create({
  baseURL: '/api',
  timeout: 8000,
})

api.interceptors.request.use((config) => {
  const token = localStorage.getItem('somnia-token')
  if (token) config.headers.Authorization = `Bearer ${token}`
  return config
})

export function apiError(error: unknown, fallback = '请求失败'): string {
  if (axios.isAxiosError(error)) {
    const detail = error.response?.data?.detail
    if (typeof detail === 'string') return detail
  }
  return fallback
}
