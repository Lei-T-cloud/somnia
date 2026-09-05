import { computed, ref } from 'vue'
import { defineStore } from 'pinia'
import { CORRIDOR_CAMERAS } from '@/data/cameras'
import { requestCamera } from '@/utils/camera'

const BIND_KEY = 'somnia-corridor-camera-binds'
const rawStreams = new Map<string, MediaStream>()

export interface CameraBind {
  deviceId: string
  streamUrl: string
}

function emptyBind(): CameraBind {
  return { deviceId: '', streamUrl: '' }
}

function loadBinds(): Record<string, CameraBind> {
  const next: Record<string, CameraBind> = {}
  for (const camera of CORRIDOR_CAMERAS) next[camera.id] = emptyBind()
  const raw = localStorage.getItem(BIND_KEY)
  if (!raw) return next
  try {
    const parsed = JSON.parse(raw) as Record<string, Partial<CameraBind>>
    for (const camera of CORRIDOR_CAMERAS) {
      const row = parsed[camera.id]
      if (!row) continue
      next[camera.id] = {
        deviceId: typeof row.deviceId === 'string' ? row.deviceId : '',
        streamUrl: typeof row.streamUrl === 'string' ? sanitizeUrl(row.streamUrl) : '',
      }
    }
  } catch {
    /* 用空绑定 */
  }
  return next
}

function sanitizeUrl(value: string): string {
  const url = value.trim()
  if (!url) return ''
  try {
    const parsed = new URL(url)
    if (parsed.protocol !== 'http:' && parsed.protocol !== 'https:') return ''
    return parsed.toString()
  } catch {
    return ''
  }
}

function explainGetUserMediaError(error: unknown): string {
  const name = error instanceof DOMException ? error.name : ''
  if (name === 'NotAllowedError' || name === 'PermissionDeniedError') {
    return '浏览器或 Windows 拒绝了摄像权限。请在地址栏小锁/摄像头图标里允许，并到系统设置 → 隐私和安全性 → 相机中允许 Chrome/Edge。'
  }
  if (name === 'NotFoundError' || name === 'DevicesNotFoundError') {
    return '浏览器没找到摄像头。本机有 Integrated Camera，请确认没有关闭相机，并用 Chrome/Edge 打开页面。'
  }
  if (name === 'NotReadableError' || name === 'TrackStartError') {
    return 'Integrated Camera 被占用。请关闭会议软件、Windows 相机应用和其他打开本站的标签页后重试。'
  }
  if (name === 'OverconstrainedError' || name === 'ConstraintNotSatisfiedError') {
    return '无法匹配上次保存的摄像头，请再点一次接入，改用默认设备。'
  }
  if (name === 'SecurityError' || name === 'NotSupportedError') {
    return '当前页面不能调用摄像头。请用 Chrome / Edge 打开 http://127.0.0.1:5173/ ，不要用 Cursor 内嵌预览。'
  }
  return error instanceof Error ? `无法打开摄像头：${error.message}` : '无法打开摄像头'
}

export const useMonitorStore = defineStore('monitor', () => {
  const devices = ref<MediaDeviceInfo[]>([])
  const binds = ref<Record<string, CameraBind>>(loadBinds())
  const liveIds = ref<string[]>([])
  const error = ref('')
  const hint = ref('先点「接入本机摄像头到当前楼道」，在弹出框选择允许。')
  const revision = ref(0)

  const videoDevices = computed(() =>
    devices.value.filter((item) => item.kind === 'videoinput' && item.deviceId),
  )

  function bump() {
    liveIds.value = [...rawStreams.keys()]
    revision.value += 1
  }

  function streamOf(cameraId: string): MediaStream | null {
    void revision.value
    return rawStreams.get(cameraId) ?? null
  }

  function persist() {
    localStorage.setItem(BIND_KEY, JSON.stringify(binds.value))
  }

  async function refreshDevices() {
    if (!navigator.mediaDevices?.enumerateDevices) {
      error.value = '当前浏览器不支持摄像头 API，请改用 Chrome / Edge。'
      return
    }
    devices.value = await navigator.mediaDevices.enumerateDevices()
  }

  async function openStream(deviceId?: string): Promise<MediaStream> {
    if (deviceId) {
      try {
        return await navigator.mediaDevices.getUserMedia({
          video: { deviceId: { ideal: deviceId }, width: { ideal: 640 }, height: { ideal: 360 } },
          audio: false,
        })
      } catch {
        return requestCamera(10000)
      }
    }
    return requestCamera(10000)
  }

  function release(cameraId: string, force = false) {
    const stream = rawStreams.get(cameraId)
    if (!stream) return
    const deviceId = binds.value[cameraId]?.deviceId
    const shared = [...rawStreams.entries()].some(
      ([id, item]) => id !== cameraId && item === stream && binds.value[id]?.deviceId === deviceId,
    )
    if (!shared || force) stream.getTracks().forEach((track) => track.stop())
    rawStreams.delete(cameraId)
  }

  function putStream(cameraId: string, stream: MediaStream, deviceId: string) {
    rawStreams.set(cameraId, stream)
    binds.value[cameraId] = { ...(binds.value[cameraId] ?? emptyBind()), deviceId }
    persist()
    bump()
  }

  async function startDevice(cameraId: string, deviceId: string) {
    if (!CORRIDOR_CAMERAS.some((item) => item.id === cameraId)) return
    if (!deviceId) {
      release(cameraId)
      binds.value[cameraId] = { ...(binds.value[cameraId] ?? emptyBind()), deviceId: '' }
      persist()
      bump()
      return
    }
    const reused = [...rawStreams.entries()].find(
      ([id, stream]) => id !== cameraId && stream && binds.value[id]?.deviceId === deviceId,
    )
    if (reused?.[1]) {
      rawStreams.set(cameraId, reused[1])
      binds.value[cameraId] = { ...(binds.value[cameraId] ?? emptyBind()), deviceId }
      persist()
      bump()
      return
    }
    const stream = await openStream(deviceId)
    release(cameraId)
    const usedId = stream.getVideoTracks()[0]?.getSettings().deviceId || deviceId
    putStream(cameraId, stream, usedId)
    await refreshDevices()
  }

  function acceptStream(cameraId: string, stream: MediaStream) {
    if (!CORRIDOR_CAMERAS.some((item) => item.id === cameraId)) {
      stream.getTracks().forEach((track) => track.stop())
      return
    }
    release(cameraId)
    const usedId = stream.getVideoTracks()[0]?.getSettings().deviceId || 'default'
    putStream(cameraId, stream, usedId)
    hint.value = '本机摄像头已接入当前楼道。'
    error.value = ''
    void refreshDevices()
  }

  async function attachDefault(cameraId: string) {
    error.value = ''
    hint.value = '正在请求摄像头权限…'
    try {
      const preferred = binds.value[cameraId]?.deviceId || undefined
      const stream = await openStream(preferred)
      const usedId = stream.getVideoTracks()[0]?.getSettings().deviceId || preferred || 'default'
      release(cameraId)
      putStream(cameraId, stream, usedId)
      await refreshDevices()
      const label = videoDevices.value.find((item) => item.deviceId === usedId)?.label || 'Integrated Camera'
      hint.value = `已接入：${label}。若画面仍黑，请确认没有用 Cursor 内嵌预览打开本页。`
    } catch (caught) {
      error.value = explainGetUserMediaError(caught)
      hint.value = ''
    }
  }

  async function setDevice(cameraId: string, deviceId: string) {
    error.value = ''
    hint.value = ''
    try {
      await startDevice(cameraId, deviceId)
      if (deviceId) hint.value = '该楼道已切换到所选本机摄像头。'
    } catch (caught) {
      error.value = explainGetUserMediaError(caught)
    }
  }

  function setStreamUrl(cameraId: string, url: string) {
    if (!CORRIDOR_CAMERAS.some((item) => item.id === cameraId)) return
    binds.value[cameraId] = { ...(binds.value[cameraId] ?? emptyBind()), streamUrl: sanitizeUrl(url) }
    persist()
    bump()
  }

  async function restore() {
    if (!window.isSecureContext) {
      error.value = '请用 Chrome / Edge 打开 http://127.0.0.1:5173/ 。Cursor 内嵌预览通常无法调用摄像头。'
      return
    }
    await refreshDevices()
    if (!videoDevices.value.length) {
      hint.value = '尚未授权。点顶部「接入 nF 走廊」，在弹出框选择允许。'
    }
  }

  function disconnect(cameraId: string) {
    release(cameraId)
    binds.value[cameraId] = { ...(binds.value[cameraId] ?? emptyBind()), deviceId: '' }
    persist()
    bump()
    hint.value = '已断开该楼道摄像头。'
  }

  function shutdown() {
    for (const id of [...rawStreams.keys()]) release(id, true)
    bump()
  }

  return {
    devices,
    videoDevices,
    binds,
    liveIds,
    revision,
    error,
    hint,
    streamOf,
    refreshDevices,
    acceptStream,
    attachDefault,
    disconnect,
    setDevice,
    setStreamUrl,
    restore,
    shutdown,
  }
})
