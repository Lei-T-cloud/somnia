<script setup lang="ts">
import { computed, ref } from 'vue'
import { describeRoomStatus } from '@/engine/status'
import type { RoomState } from '@/types'

const props = defineProps<{
  rooms: RoomState[]
  selectedId: string | null
  portraitMap: Record<string, boolean>
}>()

const emit = defineEmits<{
  select: [id: string]
}>()

const floor = ref<number | 'all'>('all')
const status = ref<'all' | 'pending' | 'occupied' | 'vacant'>('all')

function meta(room: RoomState) {
  return describeRoomStatus(room, Boolean(room.guestEmail && props.portraitMap[room.guestEmail]))
}

const filtered = computed(() =>
  props.rooms.filter((room) => {
    if (floor.value !== 'all' && room.floor !== floor.value) return false
    const key = meta(room).key
    if (status.value === 'vacant') return key === 'vacant'
    if (status.value === 'occupied') return key !== 'vacant'
    if (status.value === 'pending') return key === 'pending'
    return true
  }),
)

function exportCsv() {
  const header = 'id,floor,temp,humidity,targetTemp,occupied,status\n'
  const rows = filtered.value
    .map((room) =>
      [room.id, room.floor, room.env.temp, room.env.humidity, room.devices.targetTemp, room.occupied, meta(room).label].join(','),
    )
    .join('\n')
  const blob = new Blob([header + rows], { type: 'text/csv;charset=utf-8' })
  const url = URL.createObjectURL(blob)
  const link = document.createElement('a')
  link.href = url
  link.download = 'somnia-rooms.csv'
  link.click()
  URL.revokeObjectURL(url)
}
</script>

<template>
  <section class="hud-panel pane">
    <div class="panel-title">
      <span>温度查询</span>
      <em>{{ filtered.length }}/{{ rooms.length }}</em>
    </div>
    <div class="toolbar">
      <el-select v-model="floor" size="small">
        <el-option label="全部楼层" value="all" />
        <el-option :value="1" label="1F" />
        <el-option :value="2" label="2F" />
        <el-option :value="3" label="3F" />
      </el-select>
      <el-select v-model="status" size="small">
        <el-option label="全部状态" value="all" />
        <el-option label="待适配" value="pending" />
        <el-option label="在住" value="occupied" />
        <el-option label="空置" value="vacant" />
      </el-select>
      <button class="ghost-btn tight" type="button" @click="exportCsv">导出</button>
    </div>
    <ul>
      <li v-for="room in filtered" :key="room.id">
        <button type="button" :class="{ on: room.id === selectedId }" @click="emit('select', room.id)">
          <header>
            <b>{{ room.id }}</b>
            <em :class="'tone-' + meta(room).tone">{{ meta(room).label }}</em>
          </header>
          <p>
            <span>温度 {{ room.env.temp.toFixed(1) }}°C</span>
            <span>目标 {{ room.devices.targetTemp }}°C</span>
            <span>空调 {{ room.devices.acOn ? '开' : '关' }}</span>
          </p>
        </button>
      </li>
    </ul>
  </section>
</template>

<style scoped>
.pane {
  display: grid;
  grid-template-rows: auto auto minmax(0, 1fr);
  min-height: 0;
}

.toolbar {
  display: grid;
  grid-template-columns: 1fr 1fr auto;
  gap: 6px;
  padding: 8px 10px;
}

.tight {
  padding: 4px 8px;
  font-size: 12px;
}

ul {
  list-style: none;
  margin: 0;
  padding: 0 8px 8px;
  overflow: auto;
  min-height: 0;
}

button {
  width: 100%;
  margin-bottom: 6px;
  text-align: left;
  padding: 9px 10px;
  border: 1px solid var(--line);
  background: rgba(8, 14, 22, 0.72);
  color: var(--text);
  cursor: pointer;
  border-radius: 8px;
}

button.on {
  border-color: var(--line-strong);
  background: var(--cyan-dim);
}

header,
p {
  display: flex;
  justify-content: space-between;
  gap: 8px;
  margin: 0;
}

b {
  font-family: var(--mono);
}

em {
  font-style: normal;
  font-size: 11px;
}

p {
  margin-top: 6px;
  color: var(--muted);
  font-size: 11px;
  font-family: var(--mono);
}

.panel-title em {
  color: var(--muted);
  font-style: normal;
}
</style>
