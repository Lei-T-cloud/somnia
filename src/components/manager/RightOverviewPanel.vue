<script setup lang="ts">
import { computed } from 'vue'
import type { ColorMode, HotelOverview, RoomState } from '@/types'

const props = defineProps<{
  rooms: RoomState[]
  overview: HotelOverview
  colorMode: ColorMode
}>()

const emit = defineEmits<{
  'update:colorMode': [value: ColorMode]
}>()

const floors = computed(() =>
  [1, 2, 3].map((floor) => {
    const list = props.rooms.filter((room) => room.floor === floor)
    const occ = list.filter((room) => room.occupied).length
    const avg = list.reduce((sum, room) => sum + room.env.temp, 0) / Math.max(list.length, 1)
    const hot = list.some((room) => room.env.temp >= 26)
    return { floor, occ, avg: avg.toFixed(1), tone: hot ? 'warn' : 'ok' }
  }),
)
</script>

<template>
  <section class="hud-panel pane">
    <div class="panel-title"><span>运行总览</span></div>
    <div class="grid">
      <article class="ok">
        <small>在住</small>
        <strong>{{ overview.occupiedCount }}</strong>
      </article>
      <article>
        <small>空置</small>
        <strong>{{ overview.vacantCount }}</strong>
      </article>
      <article :class="overview.pendingAdaptCount ? 'alert' : 'ok'">
        <small>待适配</small>
        <strong>{{ overview.pendingAdaptCount }}</strong>
      </article>
      <article class="info">
        <small>均温</small>
        <strong>{{ overview.avgTemp }}°</strong>
      </article>
      <article v-for="item in floors" :key="item.floor" :class="item.tone">
        <small>{{ item.floor }}F</small>
        <strong>{{ item.avg }}°</strong>
        <em>在住 {{ item.occ }}</em>
      </article>
      <article class="ok">
        <small>暖通</small>
        <strong>仿真</strong>
      </article>
    </div>
    <div class="mode">
      <el-radio-group :model-value="colorMode" size="small" @update:model-value="emit('update:colorMode', $event)">
        <el-radio-button label="temp">温度着色</el-radio-button>
        <el-radio-button label="occupancy">占用着色</el-radio-button>
      </el-radio-group>
    </div>
  </section>
</template>

<style scoped>
.pane {
  display: grid;
  grid-template-rows: auto minmax(0, 1fr) auto;
  min-height: 0;
}

.grid {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 6px;
  padding: 10px;
  overflow: auto;
}

article {
  padding: 10px;
  border: 1px solid var(--line);
  background: rgba(8, 14, 22, 0.7);
  border-radius: 8px;
}

article.ok { box-shadow: inset 3px 0 0 var(--green); }
article.alert { box-shadow: inset 3px 0 0 var(--alert); }
article.warn { box-shadow: inset 3px 0 0 var(--warn); }
article.info { box-shadow: inset 3px 0 0 var(--cyan); }

small,
em {
  display: block;
  color: var(--muted);
  font-style: normal;
  font-size: 11px;
}

strong {
  display: block;
  font-family: var(--mono);
  font-size: 18px;
  margin: 4px 0 2px;
}

.mode {
  padding: 0 10px 10px;
}
</style>
