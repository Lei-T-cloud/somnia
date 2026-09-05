<script setup lang="ts">
import { computed } from 'vue'
import RoomHeatmap from './RoomHeatmap.vue'
import RoomMetricChart from './RoomMetricChart.vue'
import BuildingTrendChart from './BuildingTrendChart.vue'
import { AMBIENT_TEMP } from '@/engine/simulator'
import type { DeviceSettings, EnvTrendPoint, RoomState } from '@/types'

const props = defineProps<{
  rooms: RoomState[]
  selectedId: string | null
  trend: EnvTrendPoint[]
}>()

const emit = defineEmits<{
  select: [id: string]
  patch: [id: string, patch: Partial<DeviceSettings>]
}>()

const selected = computed(() => props.rooms.find((room) => room.id === props.selectedId) ?? null)

const stats = computed(() => {
  const temps = props.rooms.map((room) => room.env.temp)
  const avg = temps.reduce((sum, value) => sum + value, 0) / Math.max(temps.length, 1)
  return {
    avg: (Math.round(avg * 10) / 10).toFixed(1),
    max: Math.max(...temps).toFixed(1),
    min: Math.min(...temps).toFixed(1),
    hot: temps.filter((value) => value >= 25.5).length,
  }
})
</script>

<template>
  <div class="viz">
    <div class="panel-title">
      <span>温度可视化</span>
      <em>本底 {{ AMBIENT_TEMP }}°C</em>
    </div>
    <section class="stats">
      <article><small>均温</small><strong>{{ stats.avg }}°</strong></article>
      <article><small>最高</small><strong>{{ stats.max }}°</strong></article>
      <article><small>最低</small><strong>{{ stats.min }}°</strong></article>
      <article><small>偏热</small><strong>{{ stats.hot }}</strong></article>
    </section>
    <p class="hint">点击热力格或柱状图选中房间，三维模型同步高亮。</p>
    <RoomHeatmap :rooms="rooms" :selected-id="selectedId" metric="temp" @select="emit('select', $event)" />
    <div v-if="selected" class="control">
      <div class="row">
        <span>{{ selected.id }} 当前 {{ selected.env.temp }}°C</span>
        <span>目标 {{ selected.devices.targetTemp }}°C</span>
      </div>
      <el-slider
        :model-value="selected.devices.targetTemp"
        :min="18"
        :max="28"
        :step="0.5"
        @change="emit('patch', selected.id, { acOn: true, targetTemp: $event as number })"
      />
    </div>
    <RoomMetricChart :rooms="rooms" :selected-id="selectedId" metric="temp" @select="emit('select', $event)" />
    <div class="panel-title inner"><span>均温趋势</span></div>
    <BuildingTrendChart :trend="trend" />
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

.stats {
  display: grid;
  grid-template-columns: repeat(4, 1fr);
  gap: 6px;
  padding: 10px 12px 0;
}

article {
  padding: 8px;
  border: 1px solid var(--line);
  background: rgba(8, 14, 22, 0.65);
}

small {
  display: block;
  color: var(--muted);
  font-size: 11px;
}

strong {
  font-family: var(--mono);
  font-size: 16px;
}

.hint,
.row {
  margin: 8px 12px 0;
  color: var(--muted);
  font-size: 12px;
}

.row {
  display: flex;
  justify-content: space-between;
}

.control {
  padding: 0 12px 4px;
}

.inner {
  border-top: 1px solid var(--line);
}

.panel-title em {
  color: var(--muted);
  font-style: normal;
}
</style>
