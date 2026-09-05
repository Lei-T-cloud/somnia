<script setup lang="ts">
import { computed } from 'vue'
import { describeRoomStatus } from '@/engine/status'
import type { DeviceSettings, GuestRecord, RoomState } from '@/types'

const props = defineProps<{
  room: RoomState | null
  guest: GuestRecord | null
  guests: GuestRecord[]
}>()

const emit = defineEmits<{
  bind: [email: string | null]
  apply: []
  patch: [patch: Partial<DeviceSettings>]
}>()

const status = computed(() =>
  props.room ? describeRoomStatus(props.room, Boolean(props.guest?.portrait)) : null,
)
</script>

<template>
  <section class="hud-panel pane">
    <div class="panel-title">
      <span>房间调控</span>
      <em v-if="room">{{ room.id }}</em>
    </div>
    <div v-if="!room" class="empty">在幕布或左侧列表中点选房间，开始调控。</div>
    <div v-else class="body">
      <div class="feed">
        <small>LIVE · 环境仿真</small>
        <strong>{{ room.env.temp }}°C</strong>
        <p>湿度 {{ room.env.humidity }}% · 光照 {{ room.env.light }}lx · 噪音 {{ room.env.noise }}dB</p>
        <i :class="'tone-' + (status?.tone ?? 'muted')">{{ status?.label }}</i>
      </div>
      <el-select
        :model-value="room.guestEmail"
        clearable
        size="small"
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
      <div v-if="guest?.portrait" class="portrait">
        <b>{{ guest.nickname }} · {{ guest.portrait.sceneName }}</b>
        <p>{{ guest.portrait.sceneSummary }}</p>
      </div>
      <button class="gold-btn" type="button" :disabled="!guest?.portrait" @click="emit('apply')">
        一键应用睡眠场景
      </button>
      <div class="row">
        <span>空调</span>
        <el-switch :model-value="room.devices.acOn" @change="emit('patch', { acOn: $event as boolean })" />
      </div>
      <label>设定 {{ room.devices.targetTemp }}°C</label>
      <el-slider
        :model-value="room.devices.targetTemp"
        :min="18"
        :max="28"
        :step="0.5"
        @change="emit('patch', { targetTemp: $event as number })"
      />
      <div class="row">
        <span>加湿</span>
        <el-switch :model-value="room.devices.humidifierOn" @change="emit('patch', { humidifierOn: $event as boolean })" />
      </div>
    </div>
  </section>
</template>

<style scoped>
.pane {
  display: grid;
  grid-template-rows: auto minmax(0, 1fr);
  min-height: 0;
}

.body,
.empty {
  padding: 10px 12px 12px;
  overflow: auto;
}

.empty {
  color: var(--muted);
  font-size: 13px;
}

.feed {
  position: relative;
  padding: 14px;
  margin-bottom: 10px;
  border: 1px solid var(--line);
  border-radius: 10px;
  background:
    radial-gradient(circle at 20% 20%, rgba(90, 210, 255, 0.18), transparent 42%),
    #070c14;
}

.feed small,
.feed p,
label {
  color: var(--muted);
  font-size: 11px;
}

.feed strong {
  display: block;
  font-family: var(--mono);
  font-size: 28px;
  margin: 4px 0;
}

.feed i {
  font-style: normal;
  font-size: 12px;
}

.portrait {
  padding: 8px 0;
}

.portrait p {
  margin: 4px 0 0;
  color: var(--muted);
  font-size: 12px;
}

.row {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin: 8px 0 4px;
}

.panel-title em {
  color: var(--cyan);
  font-style: normal;
}
</style>
