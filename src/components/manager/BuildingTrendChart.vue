<script setup lang="ts">
import { onBeforeUnmount, onMounted, ref, watch } from 'vue'
import * as echarts from 'echarts'
import type { EnvTrendPoint } from '@/types'

const props = defineProps<{
  trend: EnvTrendPoint[]
  height?: number
}>()

const el = ref<HTMLDivElement | null>(null)
let chart: echarts.ECharts | null = null

function render() {
  if (!chart) return
  chart.setOption({
    animationDuration: 240,
    backgroundColor: 'transparent',
    legend: {
      data: ['均温', '均湿'],
      textStyle: { color: '#8b97a8', fontSize: 11 },
      top: 0,
      right: 8,
    },
    grid: { left: 36, right: 36, top: 28, bottom: 22 },
    xAxis: {
      type: 'category',
      data: props.trend.map((_, index) => `${index + 1}`),
      axisLine: { lineStyle: { color: 'rgba(62,199,255,0.25)' } },
      axisLabel: { color: '#8b97a8', fontSize: 10 },
    },
    yAxis: [
      {
        type: 'value',
        min: 18,
        max: 30,
        axisLabel: { color: '#8b97a8', fontSize: 10 },
        splitLine: { lineStyle: { color: 'rgba(62,199,255,0.06)' } },
      },
      {
        type: 'value',
        min: 35,
        max: 70,
        axisLabel: { color: '#8b97a8', fontSize: 10 },
        splitLine: { show: false },
      },
    ],
    series: [
      {
        name: '均温',
        type: 'line',
        data: props.trend.map((point) => point.temp),
        smooth: true,
        symbol: 'circle',
        symbolSize: 4,
        lineStyle: { color: '#3ec7ff', width: 1.6 },
        itemStyle: { color: '#3ec7ff' },
      },
      {
        name: '均湿',
        type: 'line',
        yAxisIndex: 1,
        data: props.trend.map((point) => point.humidity),
        smooth: true,
        symbol: 'circle',
        symbolSize: 4,
        lineStyle: { color: '#ff4d5a', width: 1.6 },
        itemStyle: { color: '#ff4d5a' },
      },
    ],
  })
}

onMounted(() => {
  if (!el.value) return
  chart = echarts.init(el.value)
  render()
  window.addEventListener('resize', resize)
})

function resize() {
  chart?.resize()
}

watch(() => props.trend, render, { deep: true })

onBeforeUnmount(() => {
  window.removeEventListener('resize', resize)
  chart?.dispose()
  chart = null
})
</script>

<template>
  <div ref="el" class="chart" :style="{ height: (height ?? 150) + 'px' }" />
</template>

<style scoped>
.chart {
  width: 100%;
}
</style>
