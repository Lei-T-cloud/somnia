import { computed, ref } from 'vue'
import { defineStore } from 'pinia'
import { api } from '@/api/client'
import type { GuestRecord, HotelService, SleepPreference, SleepPortrait } from '@/types'
import { useAuthStore } from './auth'

export const useGuestStore = defineStore('guest', () => {
  const directory = ref<GuestRecord[]>([])
  const catalog = ref<HotelService[]>([])

  const current = computed(() => {
    const auth = useAuthStore()
    if (!auth.user || auth.user.role !== 'guest') return null
    return directory.value.find((item) => item.email === auth.user?.email) ?? null
  })

  const bindableGuests = computed(() =>
    directory.value.filter((item) => item.portrait || item.nickname),
  )

  async function hydrate() {
    const { data } = await api.get<GuestRecord[]>('/guests')
    directory.value = data
  }

  async function ensureGuest(email: string, nickname: string) {
    await api.post('/guests/ensure', { email, nickname })
    await hydrate()
  }

  async function savePreference(email: string, preference: SleepPreference): Promise<SleepPortrait | null> {
    const { data } = await api.put<GuestRecord>(`/guests/${encodeURIComponent(email)}/preference`, preference)
    upsert(data)
    return data.portrait
  }

  async function loadCatalog() {
    const { data } = await api.get<HotelService[]>('/services')
    catalog.value = data
  }

  async function selectRoom(email: string, roomId: string) {
    const { data } = await api.post<GuestRecord>(`/guests/${encodeURIComponent(email)}/select-room`, { roomId })
    upsert(data)
    return data
  }

  async function saveServices(email: string, serviceIds: string[]) {
    const { data } = await api.put<GuestRecord>(`/guests/${encodeURIComponent(email)}/services`, { serviceIds })
    upsert(data)
    return data
  }

  function upsert(next: GuestRecord) {
    const index = directory.value.findIndex((item) => item.email === next.email)
    if (index >= 0) directory.value[index] = next
    else directory.value.push(next)
  }

  function getByEmail(email: string | null) {
    if (!email) return null
    return directory.value.find((item) => item.email === email) ?? null
  }

  return {
    directory,
    catalog,
    current,
    bindableGuests,
    hydrate,
    ensureGuest,
    savePreference,
    loadCatalog,
    selectRoom,
    saveServices,
    getByEmail,
  }
})
