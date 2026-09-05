import type { DeviceSettings, RoomEnvironment, RoomState } from '@/types'

export const AMBIENT_TEMP = 26.2
export const AMBIENT_HUMIDITY = 47

const LIGHT_LUX: Record<DeviceSettings['lighting'], number> = {
  off: 4,
  nightlight: 18,
  dim: 42,
  soft: 78,
}

const CURTAIN_DAYLIGHT: Record<DeviceSettings['curtain'], number> = {
  closed: 0,
  half: 22,
  open: 48,
}

const NOISE_BASE = 26
const WHITE_NOISE_DB: Record<DeviceSettings['whiteNoise'], number> = {
  off: 0,
  rain: 12,
  ocean: 11,
  fan: 9,
  music: 10,
}

function approach(current: number, target: number, rate: number): number {
  return current + (target - current) * rate
}

export function deriveLight(devices: DeviceSettings): number {
  return LIGHT_LUX[devices.lighting] + CURTAIN_DAYLIGHT[devices.curtain]
}

export function deriveNoise(devices: DeviceSettings): number {
  return NOISE_BASE + WHITE_NOISE_DB[devices.whiteNoise] + (devices.acOn ? 3 : 0)
}

export function tickEnvironment(env: RoomEnvironment, devices: DeviceSettings): RoomEnvironment {
  const tempTarget = devices.acOn ? devices.targetTemp : AMBIENT_TEMP
  const humidityTarget = devices.humidifierOn ? devices.targetHumidity : AMBIENT_HUMIDITY
  const tempRate = devices.acOn ? 0.14 : 0.035
  const humidityRate = devices.humidifierOn ? 0.12 : 0.04

  return {
    temp: round1(approach(env.temp, tempTarget, tempRate)),
    humidity: round1(approach(env.humidity, humidityTarget, humidityRate)),
    light: deriveLight(devices),
    noise: deriveNoise(devices),
  }
}

export function tickRoom(room: RoomState): RoomState {
  const env = tickEnvironment(room.env, room.devices)
  const history = [...room.history, env.temp].slice(-24)
  return { ...room, env, history }
}

export function tempToColor(temp: number): string {
  if (temp <= 20) return '#3d7ec4'
  if (temp <= 21.5) return '#3d9b8f'
  if (temp <= 23.5) return '#4fa36a'
  if (temp <= 25.5) return '#c9a24a'
  return '#d4784a'
}

export function humidityToColor(humidity: number): string {
  if (humidity < 42) return '#3d7ec4'
  if (humidity < 50) return '#3d9b8f'
  if (humidity < 58) return '#4fa36a'
  return '#3ec7ff'
}

export function occupancyColor(room: RoomState, hasPortrait: boolean): string {
  if (!room.occupied) return '#3d4a5c'
  if (hasPortrait && !room.sceneApplied) return '#ff4d5a'
  if (hasPortrait && room.sceneApplied) return '#2ecc8a'
  return '#3ec7ff'
}

function round1(value: number): number {
  return Math.round(value * 10) / 10
}
