import type { RoomState } from '@/types'

export type StatusTone = 'muted' | 'alert' | 'warn' | 'ok' | 'info'

export interface RoomStatusMeta {
  key: 'vacant' | 'pending' | 'applied' | 'occupied'
  label: string
  tone: StatusTone
}

export function describeRoomStatus(room: RoomState, hasPortrait: boolean): RoomStatusMeta {
  if (!room.occupied) return { key: 'vacant', label: '空置', tone: 'muted' }
  if (hasPortrait && !room.sceneApplied) return { key: 'pending', label: '待适配', tone: 'alert' }
  if (hasPortrait && room.sceneApplied) return { key: 'applied', label: '已适配', tone: 'ok' }
  return { key: 'occupied', label: '在住', tone: 'info' }
}

export function tempProgress(temp: number, target: number): number {
  const span = Math.max(Math.abs(target - 18), 1)
  const delta = Math.min(Math.abs(temp - target) / span, 1)
  return Math.round((1 - delta) * 100)
}
