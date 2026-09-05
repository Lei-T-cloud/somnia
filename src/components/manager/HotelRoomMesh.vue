<script setup lang="ts">
import { computed } from 'vue'
import { Html } from '@tresjs/cientos'
import { occupancyColor, tempToColor } from '@/engine/simulator'
import type { ColorMode, RoomState } from '@/types'

const props = defineProps<{
  room: RoomState
  selected: boolean
  colorMode: ColorMode
  hasPortrait: boolean
}>()

const emit = defineEmits<{
  select: [id: string]
  dblclick: [id: string]
}>()

const SLOT: Record<number, [number, number]> = {
  1: [-3.15, -3.15],
  2: [3.15, -3.15],
  3: [-3.15, 3.15],
  4: [3.15, 3.15],
}

const position = computed<[number, number, number]>(() => {
  const num = Number(props.room.id)
  const floor = Math.floor(num / 100)
  const slot = num % 100
  const [x, z] = SLOT[slot] ?? [0, 0]
  const y = (floor - 1) * 3.2 + 1.28
  return [x, y, z]
})

const color = computed(() =>
  props.colorMode === 'temp' ? tempToColor(props.room.env.temp) : occupancyColor(props.room, props.hasPortrait),
)

const emissive = computed(() => (props.selected ? '#3ec7ff' : color.value))
const emissiveIntensity = computed(() => (props.selected ? 0.5 : 0.18))
</script>

<template>
  <TresGroup :position="position">
    <TresMesh
      :cast-shadow="true"
      :receive-shadow="true"
      @click.stop="emit('select', room.id)"
      @dblclick.stop="emit('dblclick', room.id)"
    >
      <TresBoxGeometry :args="[3.55, 2.15, 3.55]" />
      <TresMeshStandardMaterial
        :color="color"
        :emissive="emissive"
        :emissive-intensity="emissiveIntensity"
        :metalness="0.12"
        :roughness="0.42"
        :transparent="true"
        :opacity="0.92"
      />
    </TresMesh>
    <Html center :distance-factor="12" :position="[0, 1.45, 0]" :occlude="false">
      <div class="lbl" :class="{ on: selected }">{{ room.id }}</div>
    </Html>
  </TresGroup>
</template>

<style scoped>
.lbl {
  font-size: 11px;
  letter-spacing: 0.08em;
  padding: 2px 6px;
  border-radius: 2px;
  color: #d9f4ff;
  background: rgba(7, 11, 20, 0.7);
  border: 1px solid rgba(62, 199, 255, 0.28);
  pointer-events: none;
  white-space: nowrap;
  font-family: "JetBrains Mono", "Cascadia Mono", monospace;
}

.lbl.on {
  color: #041018;
  background: #3ec7ff;
}
</style>
