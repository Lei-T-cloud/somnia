<script setup lang="ts">
import { computed } from 'vue'
import TempChart from './TempChart.vue'
import type { DeviceSettings, GuestRecord, RoomState } from '@/types'

const props = defineProps<{
  modelValue: boolean
  room: RoomState | null
  guest: GuestRecord | null
  guests: GuestRecord[]
}>()

const emit = defineEmits<{
  'update:modelValue': [value: boolean]
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

const title = computed(() => (props.room ? `${props.room.name} 调控` : '房间调控'))
const pending = computed(() => Boolean(props.guest?.portrait && props.room && !props.room.sceneApplied))
</script>

<template>
  <el-drawer
    :model-value="modelValue"
    :title="title"
    size="420px"
    append-to-body
    @update:model-value="emit('update:modelValue', $event)"
  >
    <div v-if="room" class="panel">
      <section class="metrics">
        <article>
          <small>温度</small>
          <strong>{{ room.env.temp }}°C</strong>
        </article>
        <article>
          <small>湿度</small>
          <strong>{{ room.env.humidity }}%</strong>
        </article>
        <article>
          <small>光照</small>
          <strong>{{ room.env.light }} lx</strong>
        </article>
        <article>
          <small>噪音</small>
          <strong>{{ room.env.noise }} dB</strong>
        </article>
      </section>

      <p class="caption">室温曲线（环境仿真）</p>
      <TempChart :history="room.history" />

      <section class="guest-box">
        <div class="row">
          <span>绑定住客</span>
          <el-tag v-if="pending" type="warning" size="small">待适配</el-tag>
          <el-tag v-else-if="room.sceneApplied" type="success" size="small">场景已应用</el-tag>
        </div>
        <el-select
          :model-value="room.guestEmail"
          clearable
          placeholder="选择住客或退房"
          @update:model-value="emit('bind', $event || null)"
        >
          <el-option
            v-for="item in guests"
            :key="item.email"
            :label="`${item.nickname}（${item.portrait ? item.portrait.sceneName : '无画像'}）`"
            :value="item.email"
          />
        </el-select>
        <div v-if="guest?.portrait" class="portrait-mini">
          <strong>{{ guest.portrait.sceneName }}</strong>
          <p>{{ guest.portrait.sceneSummary }}</p>
          <p>目标 {{ guest.portrait.settings.targetTemp }}°C / {{ guest.portrait.settings.targetHumidity }}%</p>
        </div>
        <button class="gold-btn" type="button" :disabled="!guest?.portrait" @click="emit('apply')">
          一键应用睡眠场景
        </button>
      </section>

      <section class="controls">
        <h3>设备调控</h3>
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
        <label>设定湿度 {{ room.devices.targetHumidity }}%</label>
        <el-slider
          :model-value="room.devices.targetHumidity"
          :min="35"
          :max="70"
          :step="1"
          @change="emit('patch', { targetHumidity: $event as number })"
        />
        <label>灯光</label>
        <el-select :model-value="room.devices.lighting" @change="emit('patch', { lighting: $event })">
          <el-option v-for="item in lightOptions" :key="item.value" :label="item.label" :value="item.value" />
        </el-select>
        <label>窗帘</label>
        <el-select :model-value="room.devices.curtain" @change="emit('patch', { curtain: $event })">
          <el-option v-for="item in curtainOptions" :key="item.value" :label="item.label" :value="item.value" />
        </el-select>
        <label>白噪音</label>
        <el-select :model-value="room.devices.whiteNoise" @change="emit('patch', { whiteNoise: $event })">
          <el-option v-for="item in noiseOptions" :key="item.value" :label="item.label" :value="item.value" />
        </el-select>
        <div class="row">
          <span>香氛</span>
          <el-switch :model-value="room.devices.fragranceOn" @change="emit('patch', { fragranceOn: $event as boolean })" />
        </div>
      </section>
    </div>
  </el-drawer>
</template>

<style scoped>
.panel {
  display: grid;
  gap: 16px;
}

.metrics {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 8px;
}

.metrics article {
  padding: 10px 12px;
  border-radius: 12px;
  background: #101827;
}

small {
  color: var(--muted);
}

.caption,
label {
  color: var(--muted);
  font-size: 13px;
}

.guest-box,
.controls {
  display: grid;
  gap: 10px;
  padding: 12px;
  border-radius: 14px;
  border: 1px solid var(--line);
}

.row {
  display: flex;
  justify-content: space-between;
  align-items: center;
  gap: 8px;
}

.portrait-mini p {
  margin: 6px 0 0;
  color: var(--muted);
}

h3 {
  margin: 0;
  font-size: 15px;
}
</style>
