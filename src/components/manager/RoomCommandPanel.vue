<script setup lang="ts">
import { computed } from 'vue'
import TempChart from './TempChart.vue'
import { describeRoomStatus } from '@/engine/status'
import type { DeviceSettings, GuestRecord, RoomState } from '@/types'

const props = defineProps<{
  room: RoomState
  guest: GuestRecord | null
  guests: GuestRecord[]
}>()

const emit = defineEmits<{
  close: []
  bind: [email: string | null]
  apply: []
  patch: [patch: Partial<DeviceSettings>]
}>()

const lightOptions = [
  { label: '关闭', value: 'off' },
  { label: '夜灯', value: 'nightlight' },
  { label: '微光', value: 'dim' },
  { label: '柔光', value: 'soft' },
]

const curtainOptions = [
  { label: '闭合', value: 'closed' },
  { label: '半开', value: 'half' },
  { label: '打开', value: 'open' },
]

const noiseOptions = [
  { label: '关闭', value: 'off' },
  { label: '雨声', value: 'rain' },
  { label: '海潮', value: 'ocean' },
  { label: '风扇', value: 'fan' },
  { label: '轻音乐', value: 'music' },
]

const status = computed(() => describeRoomStatus(props.room, Boolean(props.guest?.portrait)))
</script>

<template>
  <aside class="hud-panel dock-panel">
    <div class="panel-title">
      <span>{{ room.id }} · 对象属性</span>
      <button class="ghost-btn tight" type="button" @click="emit('close')">关闭</button>
    </div>
    <div class="body">
      <div class="meta">
        <span>ROOM-{{ room.id }}</span>
        <em :class="'tone-' + status.tone">{{ status.label }}</em>
      </div>
      <section class="metrics">
        <article><small>温度</small><strong>{{ room.env.temp }}°C</strong></article>
        <article><small>湿度</small><strong>{{ room.env.humidity }}%</strong></article>
        <article><small>光照</small><strong>{{ room.env.light }} lx</strong></article>
        <article><small>噪音</small><strong>{{ room.env.noise }} dB</strong></article>
      </section>
      <TempChart :history="room.history" />
      <el-select
        :model-value="room.guestEmail"
        clearable
        placeholder="绑定住客"
        @update:model-value="emit('bind', $event || null)"
      >
        <el-option
          v-for="item in guests"
          :key="item.email"
          :label="`${item.nickname}（${item.portrait ? item.portrait.sceneName : '无画像'}）`"
          :value="item.email"
        />
      </el-select>
      <p v-if="guest?.portrait" class="scene">
        {{ guest.portrait.sceneName }} · 目标 {{ guest.portrait.settings.targetTemp }}°C /
        {{ guest.portrait.settings.targetHumidity }}%
      </p>
      <button class="gold-btn" type="button" :disabled="!guest?.portrait" @click="emit('apply')">
        一键应用睡眠场景
      </button>
      <div class="row">
        <span>空调</span>
        <el-switch :model-value="room.devices.acOn" @change="emit('patch', { acOn: $event as boolean })" />
      </div>
      <label>设定温度 {{ room.devices.targetTemp }}°C</label>
      <el-slider
        :model-value="room.devices.targetTemp"
        :min="18"
        :max="28"
        :step="0.5"
        @change="emit('patch', { targetTemp: $event as number })"
      />
      <div class="row">
        <span>加湿器</span>
        <el-switch :model-value="room.devices.humidifierOn" @change="emit('patch', { humidifierOn: $event as boolean })" />
      </div>
      <el-select :model-value="room.devices.lighting" @change="emit('patch', { lighting: $event })">
        <el-option v-for="item in lightOptions" :key="item.value" :label="'灯光 · ' + item.label" :value="item.value" />
      </el-select>
      <el-select :model-value="room.devices.curtain" @change="emit('patch', { curtain: $event })">
        <el-option v-for="item in curtainOptions" :key="item.value" :label="'窗帘 · ' + item.label" :value="item.value" />
      </el-select>
      <el-select :model-value="room.devices.whiteNoise" @change="emit('patch', { whiteNoise: $event })">
        <el-option v-for="item in noiseOptions" :key="item.value" :label="'白噪音 · ' + item.label" :value="item.value" />
      </el-select>
    </div>
  </aside>
</template>

<style scoped>
.dock-panel {
  min-height: 0;
  max-height: 38vh;
  overflow: auto;
}

.body {
  display: grid;
  gap: 8px;
  padding: 10px 12px 14px;
}

.tight {
  padding: 2px 8px;
  font-size: 11px;
}

.meta,
.row {
  display: flex;
  justify-content: space-between;
  align-items: center;
  gap: 8px;
  font-size: 12px;
}

.meta span,
label {
  color: var(--muted);
  font-family: var(--mono);
  font-size: 11px;
}

.metrics {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 6px;
}

.metrics article {
  padding: 8px;
  border: 1px solid var(--line);
  background: rgba(7, 12, 20, 0.55);
}

small {
  color: var(--muted);
  font-size: 11px;
}

strong {
  display: block;
  font-family: var(--mono);
  margin-top: 4px;
}

.scene {
  margin: 0;
  color: var(--muted);
  font-size: 12px;
}
</style>
