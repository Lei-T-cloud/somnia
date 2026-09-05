<script setup lang="ts">
import { computed } from 'vue'
import RoomHeatmap from './RoomHeatmap.vue'
import RoomMetricChart from './RoomMetricChart.vue'
import OverviewKpi from './OverviewKpi.vue'
import { describeRoomStatus } from '@/engine/status'
import type { ColorMode, HotelOverview, RoomState } from '@/types'

const props = defineProps<{
  rooms: RoomState[]
  selectedId: string | null
  overview: HotelOverview
  colorMode: ColorMode
  portraitMap: Record<string, boolean>
}>()

const emit = defineEmits<{
  select: [id: string]
  'update:colorMode': [value: ColorMode]
}>()

const occupied = computed(() =>
  props.rooms
    .filter((room) => room.occupied)
    .map((room) => ({
      room,
      status: describeRoomStatus(room, Boolean(room.guestEmail && props.portraitMap[room.guestEmail])),
    })),
)
</script>

<template>
  <div class="viz">
    <div class="panel-title"><span>湿度 / 占用可视化</span></div>
    <p class="hint">点击热力格选中房间；占用列表同步房间状态。</p>
    <RoomHeatmap :rooms="rooms" :selected-id="selectedId" metric="humidity" @select="emit('select', $event)" />
    <RoomMetricChart :rooms="rooms" :selected-id="selectedId" metric="humidity" @select="emit('select', $event)" />
    <div class="panel-title inner"><span>在住状态</span></div>
    <ul>
      <li v-for="item in occupied" :key="item.room.id">
        <button type="button" :class="{ on: item.room.id === selectedId }" @click="emit('select', item.room.id)">
          <b>{{ item.room.id }}</b>
          <em :class="'tone-' + item.status.tone">{{ item.status.label }}</em>
          <span>{{ item.room.env.humidity.toFixed(0) }}%</span>
        </button>
      </li>
    </ul>
    <OverviewKpi :overview="overview" :color-mode="colorMode" @update:color-mode="emit('update:colorMode', $event)" />
  </div>
</template>

<style scoped>
.viz {
  display: grid;
  align-content: start;
  height: 100%;
  min-height: 0;
  overflow: auto;
}

.hint {
  margin: 8px 12px 0;
  color: var(--muted);
  font-size: 12px;
}

ul {
  list-style: none;
  margin: 0;
  padding: 8px 12px;
  display: grid;
  gap: 6px;
}

button {
  width: 100%;
  display: grid;
  grid-template-columns: 48px 1fr auto;
  gap: 8px;
  align-items: center;
  padding: 7px 8px;
  border: 1px solid var(--line);
  background: rgba(8, 14, 22, 0.65);
  color: var(--text);
  cursor: pointer;
}

button.on {
  border-color: var(--line-strong);
}

b {
  font-family: var(--mono);
}

em {
  font-style: normal;
  font-size: 12px;
}

span {
  color: var(--muted);
  font-family: var(--mono);
}

.inner {
  border-top: 1px solid var(--line);
}
</style>
