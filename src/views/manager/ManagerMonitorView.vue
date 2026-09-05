<script setup lang="ts">
import { computed, nextTick, onMounted, ref } from 'vue'
import { onBeforeRouteLeave } from 'vue-router'
import HotelTwinScene from '@/components/manager/HotelTwinScene.vue'
import MonitorFeedCard from '@/components/manager/MonitorFeedCard.vue'
import { CORRIDOR_CAMERAS } from '@/data/cameras'
import { useGuestStore } from '@/stores/guest'
import { useHotelStore } from '@/stores/hotel'
import { useMonitorStore } from '@/stores/monitor'
import { explainCameraError, requestCamera } from '@/utils/camera'
import type { ViewPreset } from '@/types'

const guests = useGuestStore()
const hotel = useHotelStore()
const monitor = useMonitorStore()
const viewPreset = ref<ViewPreset>('iso')
const selectedCameraId = ref(CORRIDOR_CAMERAS[0]?.id ?? 'cam-1f')
const attaching = ref(false)
const localError = ref('')
const sceneOn = ref(true)
const showSetup = ref(false)

const portraitMap = computed(() =>
  Object.fromEntries(guests.directory.map((item) => [item.email, Boolean(item.portrait)])),
)

const selectedCamera = computed(() => CORRIDOR_CAMERAS.find((item) => item.id === selectedCameraId.value) ?? CORRIDOR_CAMERAS[0])

const corridors = computed(() =>
  CORRIDOR_CAMERAS.map((camera) => {
    const rooms = hotel.rooms.filter((room) => room.floor === camera.floor)
    const count = Math.max(rooms.length, 1)
    const temp = rooms.reduce((sum, room) => sum + room.env.temp, 0) / count
    const humidity = rooms.reduce((sum, room) => sum + room.env.humidity, 0) / count
    const live = monitor.liveIds.includes(camera.id) || Boolean(monitor.binds[camera.id]?.streamUrl)
    return {
      camera,
      temp: Math.round(temp * 10) / 10,
      humidity: Math.round(humidity * 10) / 10,
      live,
      ok: temp >= 21 && temp <= 25.5 && humidity >= 40 && humidity <= 60,
    }
  }),
)

const focus = computed(() => corridors.value.find((item) => item.camera.id === selectedCameraId.value) ?? corridors.value[0])
const liveCount = computed(() => corridors.value.filter((item) => item.live).length)

onMounted(async () => {
  await hotel.hydrate()
  if (!guests.directory.length) await guests.hydrate()
  await monitor.restore()
})

onBeforeRouteLeave(() => {
  monitor.shutdown()
})

function highlight(id: string) {
  selectedCameraId.value = id
}

async function attachTo(id: string) {
  if (attaching.value) return
  selectedCameraId.value = id
  attaching.value = true
  localError.value = ''
  sceneOn.value = false
  await nextTick()
  await new Promise((resolve) => window.setTimeout(resolve, 80))
  try {
    const stream = await requestCamera(10000)
    monitor.acceptStream(id, stream)
  } catch (caught) {
    localError.value = explainCameraError(caught)
  } finally {
    attaching.value = false
    sceneOn.value = true
  }
}

function bindOf(id: string) {
  return monitor.binds[id] ?? { deviceId: '', streamUrl: '' }
}

function streamOf(id: string) {
  return monitor.streamOf(id)
}
</script>

<template>
  <main class="command">
    <header class="topbar">
      <div class="tabs">
        <b>实时监控</b>
        <span>仅走廊</span>
        <span>已接入 {{ liveCount }}/3</span>
      </div>
      <div class="actions">
        <button class="ghost-btn" type="button" @click="showSetup = !showSetup">接入设置</button>
        <button class="gold-btn" type="button" :disabled="attaching" @click="attachTo(selectedCameraId)">
          {{ attaching ? '正在打开摄像头…' : `接入 ${selectedCamera?.floor}F 走廊` }}
        </button>
      </div>
    </header>

    <p v-if="localError || monitor.error" class="banner">{{ localError || monitor.error }}</p>

    <section v-if="showSetup && selectedCamera" class="hud-panel setup">
      <div class="panel-title"><span>{{ selectedCamera.name }} 接入设置</span></div>
      <div class="setup-row">
        <label>
          本机摄像头
          <select
            :value="bindOf(selectedCamera.id).deviceId"
            @change="monitor.setDevice(selectedCamera.id, ($event.target as HTMLSelectElement).value)"
          >
            <option value="">未选择</option>
            <option v-for="device in monitor.videoDevices" :key="device.deviceId" :value="device.deviceId">
              {{ device.label || `摄像头 ${device.deviceId.slice(0, 6)}` }}
            </option>
          </select>
        </label>
        <label>
          网络画面地址
          <input
            :value="bindOf(selectedCamera.id).streamUrl"
            placeholder="https://走廊摄像头画面地址"
            @change="monitor.setStreamUrl(selectedCamera.id, ($event.target as HTMLInputElement).value)"
          />
        </label>
        <button class="ghost-btn" type="button" @click="monitor.disconnect(selectedCamera.id)">断开此路</button>
      </div>
    </section>

    <section class="stage">
      <aside class="hud-panel lanes">
        <div class="panel-title"><span>楼道</span><em>点选切换焦点</em></div>
        <button
          v-for="row in corridors"
          :key="row.camera.id"
          type="button"
          class="lane"
          :class="{ on: selectedCameraId === row.camera.id, live: row.live }"
          @click="highlight(row.camera.id)"
        >
          <b>{{ row.camera.floor }}F</b>
          <span>{{ row.live ? 'LIVE' : 'OFF' }}</span>
          <em :class="row.ok ? 'tone-ok' : 'tone-warn'">{{ row.temp }}°C</em>
        </button>
      </aside>

      <section class="hud-panel player">
        <div class="panel-title">
          <span>走廊实况</span>
          <em>{{ focus?.camera.name }}</em>
        </div>
        <MonitorFeedCard
          v-if="focus"
          size="focus"
          :camera="focus.camera"
          :stream="streamOf(focus.camera.id)"
          :stream-url="bindOf(focus.camera.id).streamUrl"
          :active="true"
          :temp="focus.temp"
          :humidity="focus.humidity"
        />
      </section>

      <section class="hud-panel locator">
        <div class="panel-title"><span>范围定位</span><em>只高亮走廊</em></div>
        <div class="map">
          <HotelTwinScene
            v-if="sceneOn"
            :rooms="hotel.rooms"
            :selected-id="null"
            color-mode="occupancy"
            :portrait-map="portraitMap"
            :view-preset="viewPreset"
            scene-mode="monitor"
            :selected-camera-id="selectedCameraId"
            @select-corridor="highlight"
            @select-camera="highlight"
          />
          <p v-else class="scene-wait">申请摄像头时已暂停三维</p>
          <div class="view-btns">
            <button type="button" :class="{ on: viewPreset === 'iso' }" @click="viewPreset = 'iso'">斜视</button>
            <button type="button" :class="{ on: viewPreset === 'top' }" @click="viewPreset = 'top'">俯视</button>
          </div>
        </div>
      </section>
    </section>

    <section class="wall">
      <MonitorFeedCard
        v-for="row in corridors"
        :key="row.camera.id"
        size="tile"
        :camera="row.camera"
        :stream="streamOf(row.camera.id)"
        :stream-url="bindOf(row.camera.id).streamUrl"
        :active="selectedCameraId === row.camera.id"
        :temp="row.temp"
        :humidity="row.humidity"
        @select="highlight(row.camera.id)"
      />
    </section>
  </main>
</template>

<style scoped>
.command {
  height: 100%;
  display: grid;
  grid-template-rows: 48px auto minmax(0, 1fr) 188px;
  overflow: hidden;
}

.topbar,
.tabs,
.actions {
  display: flex;
  align-items: center;
  gap: 10px;
}

.topbar {
  justify-content: space-between;
  padding: 0 16px;
  border-bottom: 1px solid var(--line);
  background: rgba(7, 11, 18, 0.72);
}

.tabs b,
.tabs span {
  padding: 5px 11px;
  font-size: 12px;
  letter-spacing: 0.1em;
  border-radius: 999px;
}

.tabs b {
  color: #041018;
  background: var(--cyan);
}

.tabs span {
  color: var(--muted);
  border: 1px solid var(--line);
}

.banner {
  margin: 0;
  padding: 8px 14px;
  color: var(--alert);
  background: var(--alert-dim);
}

.setup {
  margin: 8px 8px 0;
}

.setup-row {
  display: grid;
  grid-template-columns: 1fr 1fr auto;
  gap: 10px;
  padding: 10px 12px 12px;
  align-items: end;
}

label {
  display: grid;
  gap: 4px;
  color: var(--muted);
  font-size: 12px;
}

select,
input {
  border: 1px solid var(--line);
  background: #070b12;
  color: var(--text);
  padding: 7px 9px;
  border-radius: 8px;
}

.stage {
  display: grid;
  grid-template-columns: 92px minmax(0, 1.4fr) minmax(280px, 1fr);
  gap: 10px;
  padding: 10px 10px 0;
  min-height: 0;
}

.lanes,
.player,
.locator,
.map {
  min-height: 0;
}

.player {
  display: grid;
  grid-template-rows: auto minmax(0, 1fr);
}

.lane {
  display: grid;
  justify-items: center;
  gap: 4px;
  width: calc(100% - 12px);
  margin: 8px 6px;
  padding: 10px 4px;
  border: 1px solid var(--line);
  background: transparent;
  color: inherit;
  cursor: pointer;
  border-radius: 10px;
}

.lane b {
  font-size: 20px;
}

.lane span,
.lane em {
  font-size: 11px;
  font-style: normal;
  font-family: var(--mono);
  color: var(--alert);
}

.lane.live span {
  color: var(--green);
}

.lane.on {
  border-color: var(--cyan);
  background: var(--cyan-dim);
}

.map {
  position: relative;
  height: calc(100% - 36px);
  background: #070b12;
}

.scene-wait {
  height: 100%;
  display: grid;
  place-items: center;
  color: var(--muted);
}

.view-btns {
  position: absolute;
  top: 8px;
  right: 8px;
  z-index: 3;
  display: flex;
  gap: 6px;
}

.view-btns button {
  border: 1px solid var(--line);
  background: rgba(8, 14, 22, 0.78);
  color: var(--muted);
  padding: 5px 10px;
  cursor: pointer;
  border-radius: 999px;
}

.view-btns button.on {
  color: #041018;
  background: var(--cyan);
}

.wall {
  display: grid;
  grid-template-columns: 1fr 1fr 1fr;
  gap: 10px;
  padding: 10px;
  min-height: 0;
}

.panel-title em {
  color: var(--muted);
  font-style: normal;
}

@media (max-width: 1100px) {
  .command {
    grid-template-rows: 48px auto auto auto;
    overflow: auto;
  }

  .stage,
  .setup-row,
  .wall {
    grid-template-columns: 1fr;
  }

  .map,
  .focus .stage {
    min-height: 240px;
  }
}
</style>
