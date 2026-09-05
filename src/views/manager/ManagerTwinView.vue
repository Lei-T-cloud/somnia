<script setup lang="ts">
import { computed, onBeforeUnmount, onMounted, ref } from 'vue'
import { ElMessage } from 'element-plus'
import HotelTwinScene from '@/components/manager/HotelTwinScene.vue'
import LeftQueryPanel from '@/components/manager/LeftQueryPanel.vue'
import LeftInspectPanel from '@/components/manager/LeftInspectPanel.vue'
import RightControlPanel from '@/components/manager/RightControlPanel.vue'
import RightOverviewPanel from '@/components/manager/RightOverviewPanel.vue'
import { AMBIENT_HUMIDITY, AMBIENT_TEMP } from '@/engine/simulator'
import { useGuestStore } from '@/stores/guest'
import { useHotelStore } from '@/stores/hotel'
import type { ColorMode, ViewPreset } from '@/types'

const guests = useGuestStore()
const hotel = useHotelStore()
const clock = ref('')
const viewPreset = ref<ViewPreset>('front')
let clockTimer: number | null = null

const portraitMap = computed(() =>
  Object.fromEntries(guests.directory.map((item) => [item.email, Boolean(item.portrait)])),
)

const selectedGuest = computed(() => guests.getByEmail(hotel.selectedRoom?.guestEmail ?? null))
const progress = computed(() => Math.round((hotel.trend.length / 36) * 100))

onMounted(async () => {
  if (!guests.directory.length) await guests.hydrate()
  if (!hotel.rooms.length) await hotel.hydrate()
  tickClock()
  clockTimer = window.setInterval(tickClock, 1000)
})

onBeforeUnmount(() => {
  if (clockTimer != null) window.clearInterval(clockTimer)
})

function tickClock() {
  clock.value = new Date().toLocaleString('zh-CN', { hour12: false })
}

function selectRoom(id: string) {
  hotel.selectRoom(id)
}

async function applyScene() {
  if (!hotel.selectedRoomId) return
  const error = await hotel.applySleepScene(hotel.selectedRoomId)
  if (error) ElMessage.warning(error)
  else ElMessage.success('已应用睡眠场景，环境仿真开始逼近目标值')
}

</script>

<template>
  <main class="command">
    <header class="topbar">
      <div class="tabs">
        <b>实时温湿</b>
        <span>实时孪生</span>
        <span>环境仿真</span>
      </div>
      <time>{{ clock }}</time>
    </header>

    <section class="stage">
      <LeftQueryPanel
        class="q"
        :rooms="hotel.rooms"
        :selected-id="hotel.selectedRoomId"
        :portrait-map="portraitMap"
        @select="selectRoom"
      />
      <LeftInspectPanel
        class="i"
        :rooms="hotel.rooms"
        :selected-id="hotel.selectedRoomId"
        :trend="hotel.trend"
        @select="selectRoom"
      />

      <section class="curtain">
        <HotelTwinScene
          :rooms="hotel.rooms"
          :selected-id="hotel.selectedRoomId"
          :color-mode="hotel.colorMode"
          :portrait-map="portraitMap"
          :view-preset="viewPreset"
          @select="selectRoom"
        />
        <div class="view-btns">
          <button type="button" :class="{ on: viewPreset === 'front' }" @click="viewPreset = 'front'">正视</button>
          <button type="button" :class="{ on: viewPreset === 'iso' }" @click="viewPreset = 'iso'">斜视</button>
          <button type="button" :class="{ on: viewPreset === 'top' }" @click="viewPreset = 'top'">俯视</button>
        </div>
        <div class="weather">
          <small>仿真环境</small>
          <strong>{{ AMBIENT_TEMP }}°C</strong>
          <em>湿度 {{ AMBIENT_HUMIDITY }}% · 非真实气象</em>
        </div>
      </section>

      <RightControlPanel
        class="c"
        :room="hotel.selectedRoom"
        :guest="selectedGuest"
        :guests="guests.bindableGuests"
        @bind="hotel.bindGuest(hotel.selectedRoomId!, $event)"
        @apply="applyScene"
        @patch="hotel.updateDevices(hotel.selectedRoomId!, $event)"
      />
      <RightOverviewPanel
        class="o"
        :rooms="hotel.rooms"
        :overview="hotel.overview"
        :color-mode="hotel.colorMode"
        @update:color-mode="hotel.colorMode = $event as ColorMode"
      />
    </section>

    <footer class="playback">
      <button class="gold-btn" type="button" @click="hotel.toggleSimulation()">
        {{ hotel.simulating ? '暂停仿真' : '继续仿真' }}
      </button>
      <span>环境仿真时间轴</span>
      <div class="track"><i :style="{ width: progress + '%' }" /></div>
      <em>{{ hotel.trend.length }} 步</em>
    </footer>
  </main>
</template>

<style scoped>
.command {
  height: 100%;
  display: grid;
  grid-template-rows: 48px minmax(0, 1fr) 40px;
  overflow: hidden;
}

.topbar,
.tabs {
  display: flex;
  align-items: center;
  gap: 16px;
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
  color: #042f2e;
  background: var(--cyan);
}

.tabs span {
  color: var(--muted);
  border: 1px solid var(--line);
}

time {
  font-family: var(--mono);
  color: var(--muted);
  font-size: 12px;
}

.stage {
  display: grid;
  grid-template-columns: 280px minmax(0, 1fr) 300px;
  grid-template-rows: minmax(0, 1fr) minmax(0, 1fr);
  gap: 10px;
  padding: 10px 10px 0;
  min-height: 0;
}

.q { grid-column: 1; grid-row: 1; }
.i { grid-column: 1; grid-row: 2; }
.curtain { grid-column: 2; grid-row: 1 / 3; }
.c { grid-column: 3; grid-row: 1; }
.o { grid-column: 3; grid-row: 2; }

.curtain {
  position: relative;
  min-height: 0;
  border: 1px solid var(--line);
  border-radius: var(--radius);
  background: #070b12;
  overflow: hidden;
}

.view-btns {
  position: absolute;
  top: 12px;
  right: 12px;
  z-index: 3;
  display: flex;
  gap: 6px;
}

.view-btns button,
.weather {
  border: 1px solid var(--line);
  background: rgba(8, 14, 22, 0.78);
  color: var(--muted);
  padding: 6px 10px;
  cursor: pointer;
  font-size: 12px;
  border-radius: 999px;
}

.view-btns button.on {
  color: #041018;
  background: var(--cyan);
}

.weather {
  position: absolute;
  right: 12px;
  bottom: 12px;
  z-index: 3;
  cursor: default;
  border-radius: 12px;
}

.weather small,
.weather em {
  display: block;
  font-style: normal;
}

.weather strong {
  display: block;
  font-family: var(--mono);
  font-size: 20px;
  color: var(--text);
}

.playback {
  display: grid;
  grid-template-columns: auto auto minmax(0, 1fr) auto;
  align-items: center;
  gap: 12px;
  padding: 0 12px;
  border-top: 1px solid var(--line);
  font-size: 12px;
  color: var(--muted);
}

.track {
  height: 5px;
  background: rgba(90, 210, 255, 0.12);
  border-radius: 99px;
  overflow: hidden;
}

.track i {
  display: block;
  height: 100%;
  background: linear-gradient(90deg, #3ad49a, var(--cyan));
}

@media (max-width: 1180px) {
  .stage {
    grid-template-columns: 1fr;
    grid-template-rows: none;
    overflow: auto;
  }

  .q,
  .i,
  .curtain,
  .c,
  .o {
    grid-column: auto;
    grid-row: auto;
    min-height: 320px;
  }
}
</style>
