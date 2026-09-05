export type UserRole = 'guest' | 'manager'

export type StayScene = 'business' | 'wellness' | 'family' | 'leisure'
export type AgeGroup = '18-25' | '26-35' | '36-50' | '51+'
export type Gender = 'male' | 'female' | 'other'
export type LightPref = 'dark' | 'dim' | 'nightlight'
export type SoundPref = 'silent' | 'white-noise' | 'soft-music'
export type Firmness = 'soft' | 'medium' | 'firm'
export type SleepIssue = 'insomnia' | 'light-sleeper' | 'snoring' | 'allergy'

export type SceneId = 'deep-aid' | 'business-quick' | 'wellness'
export type LightingLevel = 'off' | 'nightlight' | 'dim' | 'soft'
export type CurtainLevel = 'closed' | 'half' | 'open'
export type WhiteNoiseKind = 'off' | 'rain' | 'ocean' | 'fan' | 'music'
export type ColorMode = 'temp' | 'occupancy'
export type ViewPreset = 'front' | 'iso' | 'top'
export type TwinSceneMode = 'climate' | 'monitor'

export interface CorridorCoverage {
  center: [number, number, number]
  size: [number, number, number]
}

export interface CorridorCamera {
  id: string
  floor: number
  name: string
  zone: 'corridor'
  position: [number, number, number]
  coverages: CorridorCoverage[]
}

export interface SessionUser {
  email: string
  role: UserRole
  nickname: string
  inviteCode?: string
}

export interface AccountRecord {
  email: string
  password: string
  role: UserRole
  nickname: string
}

export interface SleepPreference {
  nickname: string
  gender: Gender
  ageGroup: AgeGroup
  stayScene: StayScene
  bedtime: string
  wakeup: string
  preferredTemp: number
  preferredHumidity: number
  light: LightPref
  sound: SoundPref
  pillow: Firmness
  mattress: Firmness
  issues: SleepIssue[]
  fragrance: string
  bedtimeHabit: string
}

export interface DeviceSettings {
  acOn: boolean
  targetTemp: number
  targetHumidity: number
  humidifierOn: boolean
  lighting: LightingLevel
  curtain: CurtainLevel
  whiteNoise: WhiteNoiseKind
  fragranceOn: boolean
}

export interface SleepPortrait {
  sceneId: SceneId
  sceneName: string
  sceneSummary: string
  reasons: string[]
  settings: DeviceSettings
  tags: string[]
}

export interface GuestRecord {
  email: string
  nickname: string
  preference: SleepPreference | null
  portrait: SleepPortrait | null
  selectedRoomId: string | null
  serviceIds: string[]
  updatedAt: string | null
}

export interface HotelService {
  id: string
  name: string
  group: string
  description: string
}

export interface ServiceRequest {
  roomId: string
  roomName: string
  floor: number
  photoUrl: string | null
  completed: boolean
  guestEmail: string
  nickname: string
  gender: string | null
  ageGroup: string | null
  stayScene: string | null
  fragrance: string
  bedtimeHabit: string
  services: HotelService[]
  updatedAt: string | null
}

export interface RoomEnvironment {
  temp: number
  humidity: number
  light: number
  noise: number
}

export interface RoomState {
  id: string
  floor: number
  name: string
  occupied: boolean
  guestEmail: string | null
  sceneApplied: boolean
  photoUrl: string | null
  env: RoomEnvironment
  devices: DeviceSettings
  history: number[]
}

export interface HotelOverview {
  occupiedCount: number
  vacantCount: number
  avgTemp: number
  avgHumidity: number
  pendingAdaptCount: number
}

export interface EnvTrendPoint {
  temp: number
  humidity: number
}
