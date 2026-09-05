<script setup lang="ts">
import { humidityToColor, tempToColor } from '@/engine/simulator'
import type { RoomState } from '@/types'

const props = defineProps<{
  rooms: RoomState[]
  selectedId: string | null
  metric: 'temp' | 'humidity'
}>()

const emit = defineEmits<{
  select: [id: string]
}>()

function roomsOn(floor: number) {
  return props.rooms
    .filter((room) => room.floor === floor)
    .slice()
    .sort((a, b) => a.id.localeCompare(b.id))
}

function colorOf(room: RoomState) {
  return props.metric === 'temp' ? tempToColor(room.env.temp) : humidityToColor(room.env.humidity)
}

function labelOf(room: RoomState) {
  return props.metric === 'temp' ? `${room.env.temp.toFixed(1)}°` : `${room.env.humidity.toFixed(0)}%`
}
</script>

<template>
  <div class="heatmap">
    <div v-for="floor in [3, 2, 1]" :key="floor" class="floor">
      <b>{{ floor }}F</b>
      <div class="cells">
        <button
          v-for="room in roomsOn(floor)"
          :key="room.id"
          type="button"
          :class="{ on: room.id === selectedId }"
          :style="{ background: colorOf(room) + '48', borderColor: colorOf(room) }"
          @click="emit('select', room.id)"
        >
          <span>{{ room.id }}</span>
          <strong>{{ labelOf(room) }}</strong>
        </button>
      </div>
    </div>
  </div>
</template>

<style scoped>
.heatmap {
  display: grid;
  gap: 10px;
  padding: 10px 12px;
}

.floor {
  display: grid;
  grid-template-columns: 28px 1fr;
  gap: 8px;
  align-items: center;
}

b {
  color: var(--muted);
  font-family: var(--mono);
  font-size: 12px;
}

.cells {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 6px;
}

button {
  text-align: left;
  padding: 8px;
  border-radius: 3px;
  border: 1px solid transparent;
  color: var(--text);
  cursor: pointer;
}

button.on {
  outline: 1px solid #fff;
  box-shadow: 0 0 12px rgba(255, 255, 255, 0.18);
}

span {
  display: block;
  font-size: 11px;
  color: var(--muted);
}

strong {
  font-family: var(--mono);
  font-size: 15px;
}
</style>
