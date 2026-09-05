import { computed, ref } from 'vue'
import { defineStore } from 'pinia'
import { api, apiError } from '@/api/client'
import type { ColorMode, DeviceSettings, EnvTrendPoint, HotelOverview, RoomState, ServiceRequest } from '@/types'
import { useGuestStore } from './guest'

export const useHotelStore = defineStore('hotel', () => {
  const rooms = ref<RoomState[]>([])
  const selectedRoomId = ref<string | null>(null)
  const colorMode = ref<ColorMode>('temp')
  const simulating = ref(false)
  const trend = ref<EnvTrendPoint[]>([])
  const serviceRequests = ref<ServiceRequest[]>([])
  let pollTimer: number | null = null

  const selectedRoom = computed(() => rooms.value.find((room) => room.id === selectedRoomId.value) ?? null)

  const overview = computed<HotelOverview>(() => {
    const guests = useGuestStore()
    const occupied = rooms.value.filter((room) => room.occupied)
    const pending = occupied.filter((room) => {
      const guest = guests.getByEmail(room.guestEmail)
      return Boolean(guest?.portrait) && !room.sceneApplied
    })
    const count = Math.max(rooms.value.length, 1)
    const avgTemp = rooms.value.reduce((sum, room) => sum + room.env.temp, 0) / count
    const avgHumidity = rooms.value.reduce((sum, room) => sum + room.env.humidity, 0) / count
    return {
      occupiedCount: occupied.length,
      vacantCount: rooms.value.length - occupied.length,
      avgTemp: Math.round(avgTemp * 10) / 10,
      avgHumidity: Math.round(avgHumidity * 10) / 10,
      pendingAdaptCount: pending.length,
    }
  })

  function replaceRoom(next: RoomState) {
    const index = rooms.value.findIndex((room) => room.id === next.id)
    if (index >= 0) rooms.value[index] = next
  }

  async function hydrate() {
    const [roomRes, trendRes] = await Promise.all([api.get<RoomState[]>('/rooms'), api.get<EnvTrendPoint[]>('/hotel/trend')])
    rooms.value = roomRes.data
    trend.value = trendRes.data
  }

  function selectRoom(id: string | null) {
    selectedRoomId.value = id
  }

  async function updateDevices(id: string, patch: Partial<DeviceSettings>) {
    const { data } = await api.patch<RoomState>(`/rooms/${id}/devices`, patch)
    replaceRoom(data)
  }

  async function uploadPhoto(id: string, file: File) {
    const body = new FormData()
    body.append('file', file)
    const { data } = await api.post<RoomState>(`/rooms/${id}/photo`, body)
    replaceRoom(data)
    return data
  }

  async function fetchServiceRequests() {
    const { data } = await api.get<ServiceRequest[]>('/hotel/service-requests')
    serviceRequests.value = data
  }

  async function setRequestCompleted(roomId: string, completed: boolean) {
    const { data } = await api.post<ServiceRequest>(`/hotel/service-requests/${roomId}/complete`, { completed })
    const index = serviceRequests.value.findIndex((item) => item.roomId === roomId)
    if (index >= 0) serviceRequests.value[index] = data
    else serviceRequests.value.push(data)
    return data
  }

  async function bindGuest(id: string, email: string | null) {
    const { data } = await api.post<RoomState>(`/rooms/${id}/bind`, { email })
    replaceRoom(data)
  }

  async function checkout(id: string) {
    await bindGuest(id, null)
  }

  async function applySleepScene(id: string): Promise<string | null> {
    try {
      const { data } = await api.post<RoomState>(`/rooms/${id}/apply-scene`)
      replaceRoom(data)
      return null
    } catch (error) {
      return apiError(error, '无法应用睡眠场景')
    }
  }

  async function poll() {
    try {
      await Promise.all([hydrate(), useGuestStore().hydrate()])
    } catch {
      /* 下一轮再拉 */
    }
  }

  async function startSimulation() {
    await api.post('/hotel/simulation', { running: true })
    simulating.value = true
    await hydrate()
    if (pollTimer == null) pollTimer = window.setInterval(poll, 1200)
  }

  async function stopSimulation() {
    if (pollTimer != null) {
      window.clearInterval(pollTimer)
      pollTimer = null
    }
    simulating.value = false
    try {
      await api.post('/hotel/simulation', { running: false })
    } catch {
      /* 离开页面时后端可能仍在跑，可接受 */
    }
  }

  async function toggleSimulation() {
    if (simulating.value) await stopSimulation()
    else await startSimulation()
  }

  return {
    rooms,
    selectedRoomId,
    selectedRoom,
    colorMode,
    simulating,
    overview,
    trend,
    serviceRequests,
    hydrate,
    selectRoom,
    updateDevices,
    uploadPhoto,
    fetchServiceRequests,
    setRequestCompleted,
    bindGuest,
    checkout,
    applySleepScene,
    startSimulation,
    stopSimulation,
    toggleSimulation,
  }
})
