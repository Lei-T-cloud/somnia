import { deriveSleepPortrait } from '@/engine/sleepScene'
import type { DeviceSettings, GuestRecord, RoomState, SleepPreference } from '@/types'

function settings(partial: Partial<DeviceSettings>): DeviceSettings {
  return {
    acOn: true,
    targetTemp: 23,
    targetHumidity: 50,
    humidifierOn: false,
    lighting: 'dim',
    curtain: 'half',
    whiteNoise: 'off',
    fragranceOn: false,
    ...partial,
  }
}

function pref(partial: SleepPreference): SleepPreference {
  return partial
}

const linPref = pref({
  nickname: '林晚宁',
  gender: 'female',
  ageGroup: '26-35',
  stayScene: 'leisure',
  bedtime: '23:30',
  wakeup: '08:00',
  preferredTemp: 21.5,
  preferredHumidity: 50,
  light: 'dark',
  sound: 'white-noise',
  pillow: 'medium',
  mattress: 'soft',
  issues: ['insomnia', 'light-sleeper'],
  fragrance: '薰衣草',
  bedtimeHabit: '睡前阅读二十分钟',
})

const zhouPref = pref({
  nickname: '周启明',
  gender: 'male',
  ageGroup: '36-50',
  stayScene: 'business',
  bedtime: '00:30',
  wakeup: '06:30',
  preferredTemp: 23,
  preferredHumidity: 45,
  light: 'nightlight',
  sound: 'silent',
  pillow: 'firm',
  mattress: 'medium',
  issues: [],
  fragrance: '',
  bedtimeHabit: '回邮件后即睡',
})

const suPref = pref({
  nickname: '苏清和',
  gender: 'female',
  ageGroup: '51+',
  stayScene: 'wellness',
  bedtime: '21:30',
  wakeup: '06:30',
  preferredTemp: 24,
  preferredHumidity: 55,
  light: 'dim',
  sound: 'white-noise',
  pillow: 'soft',
  mattress: 'soft',
  issues: ['allergy'],
  fragrance: '雪松',
  bedtimeHabit: '温水泡脚',
})

function guest(email: string, preference: SleepPreference, selectedRoomId: string | null, serviceIds: string[]): GuestRecord {
  return {
    email,
    nickname: preference.nickname,
    preference,
    portrait: deriveSleepPortrait(preference),
    selectedRoomId,
    serviceIds,
    updatedAt: '2026-09-05T10:00:00.000Z',
  }
}

export const SEED_GUESTS: GuestRecord[] = [
  guest('guest@somnia.demo', linPref, '302', ['fragrance-setup', 'white-noise-device', 'extra-duvet', 'late-checkout']),
  guest('zhou@somnia.demo', zhouPref, '201', ['wake-up', 'late-checkout', 'extra-pillow-firm']),
  guest('su@somnia.demo', suPref, '104', ['air-purifier', 'sleep-drink', 'extra-pillow-soft']),
  {
    email: 'chen@somnia.demo',
    nickname: '陈途',
    preference: null,
    portrait: null,
    selectedRoomId: '103',
    serviceIds: [],
    updatedAt: null,
  },
]

function room(
  id: string,
  floor: number,
  occupied: boolean,
  guestEmail: string | null,
  sceneApplied: boolean,
  temp: number,
  humidity: number,
  devices: DeviceSettings,
): RoomState {
  return {
    id,
    floor,
    name: `${id} 房`,
    occupied,
    guestEmail,
    sceneApplied,
    photoUrl: null,
    env: {
      temp,
      humidity,
      light: 20,
      noise: 28,
    },
    devices,
    history: [temp],
  }
}

export const SEED_ROOMS: RoomState[] = [
  room('101', 1, false, null, false, 25.8, 46, settings({ acOn: false, targetTemp: 24 })),
  room('102', 1, false, null, false, 24.6, 48, settings({ acOn: false })),
  room('103', 1, true, 'chen@somnia.demo', false, 26.4, 44, settings({ acOn: true, targetTemp: 24 })),
  room('104', 1, true, 'su@somnia.demo', true, 24.2, 54, deriveSleepPortrait(suPref).settings),
  room('201', 2, true, 'zhou@somnia.demo', true, 23.4, 46, deriveSleepPortrait(zhouPref).settings),
  room('202', 2, false, null, false, 25.1, 47, settings({ acOn: false })),
  room('203', 2, true, null, false, 27.1, 43, settings({ acOn: false, lighting: 'soft', curtain: 'open' })),
  room('204', 2, false, null, false, 22.8, 51, settings({ acOn: true, targetTemp: 22 })),
  room('301', 3, false, null, false, 24.9, 49, settings({ acOn: false })),
  room('302', 3, true, 'guest@somnia.demo', false, 26.8, 45, settings({ acOn: true, targetTemp: 25, lighting: 'soft' })),
  room('303', 3, false, null, false, 21.6, 52, settings({ acOn: true, targetTemp: 21.5 })),
  room('304', 3, false, null, false, 25.4, 48, settings({ acOn: false })),
]
