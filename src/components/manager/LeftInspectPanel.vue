<script setup lang="ts">
import BuildingTrendChart from './BuildingTrendChart.vue'
import { tempToColor } from '@/engine/simulator'
import type { EnvTrendPoint, RoomState } from '@/types'

defineProps<{
  rooms: RoomState[]
  selectedId: string | null
  trend: EnvTrendPoint[]
}>()

const emit = defineEmits<{
  select: [id: string]
}>()
</script>

<template>
  <section class="hud-panel pane">
    <div class="panel-title"><span>温度趋势 / 房间快照</span></div>
    <BuildingTrendChart :trend="trend" :height="118" />
    <div class="shots">
      <button
        v-for="room in rooms"
        :key="room.id"
        type="button"
        :class="{ on: room.id === selectedId }"
        :style="{ background: tempToColor(room.env.temp) + '55', borderColor: tempToColor(room.env.temp) }"
        @click="emit('select', room.id)"
      >
        <span>{{ room.id }}</span>
        <strong>{{ room.env.temp.toFixed(1) }}°</strong>
      </button>
    </div>
  </section>
</template>

<style scoped>
.pane {
  display: grid;
  grid-template-rows: auto auto minmax(0, 1fr);
  min-height: 0;
}

.shots {
  display: grid;
  grid-template-columns: repeat(4, 1fr);
  gap: 6px;
  padding: 8px 10px 10px;
  min-height: 0;
  overflow: auto;
}

button {
  min-height: 48px;
  border: 1px solid transparent;
  color: var(--text);
  cursor: pointer;
  text-align: left;
  padding: 6px;
  border-radius: 8px;
}

button.on {
  outline: 1px solid #fff;
}

span {
  display: block;
  font-size: 10px;
  color: var(--muted);
}

strong {
  font-family: var(--mono);
  font-size: 13px;
}

.pane :deep(.chart) {
  height: 120px;
}
</style>
