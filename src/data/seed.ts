import type { DeviceSettings, GuestRecord, RoomState } from '@/types'

function settings(partial: Partial<DeviceSettings> = {}): DeviceSettings {
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

function room(id: string, floor: number, temp: number, humidity: number, devices: DeviceSettings): RoomState {
  return {
    id,
    floor,
    name: `${id} 房`,
    occupied: false,
    guestEmail: null,
    sceneApplied: false,
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

export const SEED_GUESTS: GuestRecord[] = []

export const SEED_ROOMS: RoomState[] = [
  room('101', 1, 23.5, 50, settings({ acOn: false, targetTemp: 24 })),
  room('102', 1, 23.5, 50, settings({ acOn: false })),
  room('103', 1, 23.5, 50, settings()),
  room('104', 1, 23.5, 50, settings()),
  room('201', 2, 23.5, 50, settings()),
  room('202', 2, 23.5, 50, settings({ acOn: false })),
  room('203', 2, 23.5, 50, settings({ lighting: 'soft', curtain: 'open' })),
  room('204', 2, 23.5, 50, settings({ targetTemp: 22 })),
  room('301', 3, 23.5, 50, settings({ acOn: false })),
  room('302', 3, 23.5, 50, settings()),
  room('303', 3, 23.5, 50, settings({ targetTemp: 21.5 })),
  room('304', 3, 23.5, 50, settings({ acOn: false })),
]
