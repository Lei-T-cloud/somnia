<script setup lang="ts">
import { describeRoomStatus, tempProgress } from '@/engine/status'
import type { RoomState } from '@/types'

defineProps<{
  rooms: RoomState[]
  selectedId: string | null
  portraitMap: Record<string, boolean>
}>()

const emit = defineEmits<{
  select: [id: string]
}>()
</script>

<template>
  <div class="grid">
    <button
      v-for="room in rooms"
      :key="room.id"
      type="button"
      class="card"
      :class="{ on: room.id === selectedId }"
      @click="emit('select', room.id)"
    >
      <header>
        <strong>{{ room.id }}</strong>
        <em :class="'tone-' + describeRoomStatus(room, Boolean(room.guestEmail && portraitMap[room.guestEmail])).tone">
          {{ describeRoomStatus(room, Boolean(room.guestEmail && portraitMap[room.guestEmail])).label }}
        </em>
      </header>
      <div class="metrics">
        <span>{{ room.env.temp.toFixed(1) }}°C</span>
        <span>{{ room.env.humidity.toFixed(0) }}%</span>
      </div>
      <div class="bar">
        <i :style="{ width: tempProgress(room.env.temp, room.devices.targetTemp) + '%' }" />
      </div>
      <footer>
        <small>空调 {{ room.devices.acOn ? '开' : '关' }}</small>
        <small>灯 {{ room.devices.lighting === 'off' ? '关' : '开' }}</small>
      </footer>
    </button>
  </div>
</template>

<style scoped>
.grid {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 8px;
  overflow: auto;
  padding: 10px;
  min-height: 0;
}

.card {
  text-align: left;
  padding: 10px;
  border-radius: 4px;
  border: 1px solid var(--line);
  background: rgba(8, 14, 22, 0.7);
  color: var(--text);
  cursor: pointer;
}

.card.on {
  border-color: var(--line-strong);
  box-shadow: 0 0 0 1px rgba(62, 199, 255, 0.25), 0 0 16px rgba(62, 199, 255, 0.12);
}

header,
.metrics,
footer {
  display: flex;
  justify-content: space-between;
  align-items: center;
  gap: 6px;
}

header strong {
  font-family: var(--mono);
  font-size: 13px;
}

header em {
  font-style: normal;
  font-size: 11px;
}

.metrics {
  margin: 8px 0 6px;
  font-family: var(--mono);
  font-size: 15px;
}

.bar {
  height: 3px;
  background: rgba(62, 199, 255, 0.08);
  overflow: hidden;
}

.bar i {
  display: block;
  height: 100%;
  background: var(--cyan);
}

footer small {
  color: var(--muted);
  font-size: 11px;
}
</style>
