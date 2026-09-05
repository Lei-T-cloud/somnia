import type { CorridorCamera } from '@/types'

/** 仅走廊覆盖，不进入客房盒体。 */
export const CORRIDOR_CAMERAS: CorridorCamera[] = [1, 2, 3].map((floor) => {
  const y = (floor - 1) * 3.2
  return {
    id: `cam-${floor}f`,
    floor,
    name: `${floor}F 走廊摄像头`,
    zone: 'corridor',
    position: [0, y + 2.52, 5.35],
    coverages: [
      { center: [0, y + 1.2, 0], size: [11.2, 2.1, 2.15] },
      { center: [0, y + 1.2, 0], size: [2.15, 2.1, 11.2] },
    ],
  }
})
