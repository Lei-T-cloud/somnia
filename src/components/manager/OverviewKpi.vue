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
  <section class="kpi">
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
    <article>
      <small>均湿</small>
      <strong>{{ overview.avgHumidity }}%</strong>
    </article>
    <article class="mode">
      <small>着色</small>
      <el-radio-group :model-value="colorMode" size="small" @update:model-value="emit('update:colorMode', $event)">
        <el-radio-button label="temp">温度</el-radio-button>
        <el-radio-button label="occupancy">占用</el-radio-button>
      </el-radio-group>
    </article>
  </section>
</template>

<style scoped>
.kpi {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 8px;
  padding: 10px;
}

article {
  padding: 10px;
  border: 1px solid var(--line);
  border-radius: 4px;
  background: rgba(8, 14, 22, 0.65);
}

article.ok { box-shadow: inset 3px 0 0 var(--green); }
article.alert { box-shadow: inset 3px 0 0 var(--alert); }
article.info { box-shadow: inset 3px 0 0 var(--cyan); }

small {
  display: block;
  color: var(--muted);
  font-size: 11px;
  letter-spacing: 0.08em;
}

strong {
  display: block;
  margin-top: 6px;
  font-family: var(--mono);
  font-size: 22px;
}

.mode {
  grid-column: 1 / -1;
}
</style>
