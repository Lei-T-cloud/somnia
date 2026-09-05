<script setup lang="ts">
import { onBeforeUnmount, onMounted, ref, watch } from 'vue'
import * as echarts from 'echarts'

const props = defineProps<{
  history: number[]
}>()

const el = ref<HTMLDivElement | null>(null)
let chart: echarts.ECharts | null = null

function render() {
  if (!chart) return
  chart.setOption({
    animationDuration: 280,
    grid: { left: 36, right: 12, top: 16, bottom: 24 },
    xAxis: {
      type: 'category',
      data: props.history.map((_, index) => `${index + 1}`),
      axisLine: { lineStyle: { color: 'rgba(62,199,255,0.28)' } },
      axisLabel: { color: '#8b97a8' },
    },
    yAxis: {
      type: 'value',
      min: 18,
      max: 30,
      axisLabel: { color: '#8b97a8' },
      splitLine: { lineStyle: { color: 'rgba(62,199,255,0.08)' } },
    },
    series: [
      {
        type: 'line',
        data: props.history,
        smooth: true,
        symbol: 'none',
        lineStyle: { color: '#3ec7ff', width: 2 },
        areaStyle: { color: 'rgba(62,199,255,0.14)' },
      },
    ],
  })
}

onMounted(() => {
  if (!el.value) return
  chart = echarts.init(el.value)
  render()
})

watch(() => props.history, render, { deep: true })

onBeforeUnmount(() => {
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
  height: 120px;
}
</style>
