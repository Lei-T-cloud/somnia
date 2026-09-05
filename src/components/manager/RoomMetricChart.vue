<script setup lang="ts">
import { onBeforeUnmount, onMounted, ref, watch } from 'vue'
import * as echarts from 'echarts'
import type { RoomState } from '@/types'

const props = defineProps<{
  rooms: RoomState[]
  selectedId: string | null
  metric: 'temp' | 'humidity'
}>()

const emit = defineEmits<{
  select: [id: string]
}>()

const el = ref<HTMLDivElement | null>(null)
let chart: echarts.ECharts | null = null

function values() {
  return [...props.rooms]
    .sort((a, b) => a.id.localeCompare(b.id))
    .map((room) => ({
      id: room.id,
      value: props.metric === 'temp' ? room.env.temp : room.env.humidity,
    }))
}

function render() {
  if (!chart) return
  const rows = values()
  const color = props.metric === 'temp' ? '#f0b429' : '#3ec7ff'
  chart.setOption({
    animationDuration: 220,
    grid: { left: 36, right: 12, top: 8, bottom: 22 },
    xAxis: {
      type: 'category',
      data: rows.map((row) => row.id),
      axisLabel: { color: '#8b97a8', fontSize: 10, rotate: 40 },
      axisLine: { lineStyle: { color: 'rgba(62,199,255,0.25)' } },
    },
    yAxis: {
      type: 'value',
      min: props.metric === 'temp' ? 18 : 35,
      max: props.metric === 'temp' ? 30 : 70,
      axisLabel: { color: '#8b97a8', fontSize: 10 },
      splitLine: { lineStyle: { color: 'rgba(62,199,255,0.06)' } },
    },
    series: [
      {
        type: 'bar',
        data: rows.map((row) => ({
          value: row.value,
          itemStyle: {
            color: row.id === props.selectedId ? '#ffffff' : color,
            opacity: row.id === props.selectedId ? 1 : 0.78,
          },
        })),
        barWidth: 10,
      },
    ],
  })
}

function onClick(params: { name?: string }) {
  if (params.name) emit('select', params.name)
}

onMounted(() => {
  if (!el.value) return
  chart = echarts.init(el.value)
  chart.on('click', onClick)
  render()
  window.addEventListener('resize', resize)
})

function resize() {
  chart?.resize()
}

watch(() => [props.rooms, props.selectedId, props.metric], render, { deep: true })

onBeforeUnmount(() => {
  window.removeEventListener('resize', resize)
  chart?.off('click', onClick)
  chart?.dispose()
  chart = null
})
</script>

<template>
  <div ref="el" class="chart" />
</template>

<style scoped>
.chart {
  width: 100%;
  height: 168px;
}
</style>
