<script setup lang="ts">
import type { ColorMode, HotelOverview } from '@/types'

defineProps<{
  overview: HotelOverview
  colorMode: ColorMode
}>()

const emit = defineEmits<{
  'update:colorMode': [value: ColorMode]
}>()
</script>

<template>
  <section class="bar">
    <article>
      <small>在住</small>
      <strong>{{ overview.occupiedCount }}</strong>
      <em>空置 {{ overview.vacantCount }}</em>
    </article>
    <article>
      <small>平均室温</small>
      <strong>{{ overview.avgTemp }}°C</strong>
      <em>环境仿真读数</em>
    </article>
    <article>
      <small>待适配偏好</small>
      <strong>{{ overview.pendingAdaptCount }}</strong>
      <em>已有画像未应用</em>
    </article>
    <article class="mode">
      <small>房间着色</small>
      <el-radio-group :model-value="colorMode" size="small" @update:model-value="emit('update:colorMode', $event)">
        <el-radio-button label="temp">温度</el-radio-button>
        <el-radio-button label="occupancy">占用</el-radio-button>
      </el-radio-group>
    </article>
  </section>
</template>

<style scoped>
.bar {
  display: grid;
  grid-template-columns: repeat(4, minmax(0, 1fr));
  gap: 10px;
}

article {
  padding: 12px 14px;
  border-radius: 14px;
  background: var(--bg-card);
  border: 1px solid var(--line);
  backdrop-filter: blur(14px);
}

small,
em {
  display: block;
  color: var(--muted);
  font-style: normal;
  font-size: 12px;
}

strong {
  display: block;
  font-size: 26px;
  margin: 4px 0;
}

@media (max-width: 900px) {
  .bar {
    grid-template-columns: 1fr 1fr;
  }
}
</style>
