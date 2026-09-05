<script setup lang="ts">
import type { SleepPortrait } from '@/types'

defineProps<{
  portrait: SleepPortrait
}>()

const lightLabel: Record<SleepPortrait['settings']['lighting'], string> = {
  off: '关闭',
  nightlight: '夜灯',
  dim: '微光',
  soft: '柔光',
}

const curtainLabel: Record<SleepPortrait['settings']['curtain'], string> = {
  closed: '闭合',
  half: '半开',
  open: '打开',
}

const noiseLabel: Record<SleepPortrait['settings']['whiteNoise'], string> = {
  off: '关闭',
  rain: '雨声',
  ocean: '海潮',
  fan: '风扇',
  music: '轻音乐',
}
</script>

<template>
  <section class="portrait">
    <header>
      <p class="eyebrow">我的睡眠画像</p>
      <h2>{{ portrait.sceneName }}</h2>
      <p>{{ portrait.sceneSummary }}</p>
      <div class="tags">
        <span v-for="tag in portrait.tags" :key="tag">{{ tag }}</span>
      </div>
    </header>

    <div class="settings">
      <article>
        <small>目标温度</small>
        <strong>{{ portrait.settings.targetTemp }}°C</strong>
      </article>
      <article>
        <small>目标湿度</small>
        <strong>{{ portrait.settings.targetHumidity }}%</strong>
      </article>
      <article>
        <small>灯光</small>
        <strong>{{ lightLabel[portrait.settings.lighting] }}</strong>
      </article>
      <article>
        <small>窗帘</small>
        <strong>{{ curtainLabel[portrait.settings.curtain] }}</strong>
      </article>
      <article>
        <small>白噪音</small>
        <strong>{{ noiseLabel[portrait.settings.whiteNoise] }}</strong>
      </article>
      <article>
        <small>空调 / 加湿</small>
        <strong>{{ portrait.settings.acOn ? '开' : '关' }} / {{ portrait.settings.humidifierOn ? '开' : '关' }}</strong>
      </article>
    </div>

    <div class="reasons">
      <h3>规则解释</h3>
      <ol>
        <li v-for="reason in portrait.reasons" :key="reason">{{ reason }}</li>
      </ol>
    </div>
  </section>
</template>

<style scoped>
.portrait {
  display: grid;
  gap: 22px;
}

.eyebrow {
  color: var(--cyan);
  letter-spacing: 0.12em;
  font-size: 12px;
  margin: 0;
  font-family: var(--mono);
}

h2 {
  margin: 6px 0 8px;
}

.tags {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
}

.tags span {
  padding: 4px 10px;
  border-radius: 2px;
  background: var(--cyan-dim);
  color: var(--cyan);
  font-size: 12px;
  border: 1px solid var(--line);
}

.settings {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(120px, 1fr));
  gap: 10px;
}

article {
  padding: 14px;
  border-radius: 12px;
  background: rgba(7, 11, 20, 0.35);
  border: 1px solid var(--line);
}

small {
  color: var(--muted);
}

strong {
  display: block;
  margin-top: 6px;
  font-size: 20px;
}

ol {
  margin: 0;
  padding-left: 18px;
  color: var(--muted);
}
</style>
