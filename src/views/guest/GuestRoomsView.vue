<script setup lang="ts">
import { computed, onMounted, ref } from 'vue'
import { ElMessage } from 'element-plus'
import { apiError } from '@/api/client'
import HotelTwinScene from '@/components/manager/HotelTwinScene.vue'
import { useAuthStore } from '@/stores/auth'
import { useGuestStore } from '@/stores/guest'
import { useHotelStore } from '@/stores/hotel'
import type { ViewPreset } from '@/types'

const auth = useAuthStore()
const guests = useGuestStore()
const hotel = useHotelStore()
const viewPreset = ref<ViewPreset>('iso')
const confirming = ref(false)

const portraitMap = computed(() =>
  Object.fromEntries(guests.directory.map((item) => [item.email, Boolean(item.portrait)])),
)

const selected = computed(() => hotel.selectedRoom)
const mine = computed(() => guests.current)
const occupiedByOther = computed(() => {
  const room = selected.value
  if (!room || !auth.user) return false
  return Boolean(room.guestEmail && room.guestEmail !== auth.user.email)
})
const alreadyMine = computed(() => selected.value?.id === mine.value?.selectedRoomId)
const roomIndex = computed(() => hotel.rooms.findIndex((room) => room.id === hotel.selectedRoomId))
const canPrev = computed(() => roomIndex.value > 0)
const canNext = computed(() => roomIndex.value >= 0 && roomIndex.value < hotel.rooms.length - 1)

onMounted(async () => {
  await hotel.hydrate()
  hotel.selectRoom(mine.value?.selectedRoomId ?? hotel.rooms[0]?.id ?? null)
})

function pick(id: string) {
  hotel.selectRoom(id)
}

function stepRoom(delta: number) {
  const next = hotel.rooms[roomIndex.value + delta]
  if (next) hotel.selectRoom(next.id)
}

async function confirm() {
  if (!auth.user || !selected.value) return
  if (occupiedByOther.value) {
    ElMessage.warning('该房间已被其他住客占用')
    return
  }
  confirming.value = true
  try {
    await guests.selectRoom(auth.user.email, selected.value.id)
    await hotel.hydrate()
    ElMessage.success(`已确认选择 ${selected.value.name}`)
  } catch (error) {
    ElMessage.error(apiError(error, '选房失败'))
  } finally {
    confirming.value = false
  }
}
</script>

<template>
  <main class="pick">
    <section class="curtain hud-panel">
      <HotelTwinScene
        :rooms="hotel.rooms"
        :selected-id="hotel.selectedRoomId"
        :color-mode="'occupancy'"
        :portrait-map="portraitMap"
        :view-preset="viewPreset"
        @select="pick"
        @dblclick="pick"
      />
      <div class="view-btns">
        <button type="button" :class="{ on: viewPreset === 'front' }" @click="viewPreset = 'front'">正视</button>
        <button type="button" :class="{ on: viewPreset === 'iso' }" @click="viewPreset = 'iso'">斜视</button>
        <button type="button" :class="{ on: viewPreset === 'top' }" @click="viewPreset = 'top'">俯视</button>
      </div>
    </section>

    <aside class="rail">
      <section class="hud-panel photo">
        <div class="panel-title"><span>房间实景</span><em>{{ selected?.name || '未选择' }}</em></div>
        <div class="switcher">
          <button type="button" class="ghost-btn" :disabled="!canPrev" @click="stepRoom(-1)">上一间</button>
          <div class="ids">
            <button
              v-for="room in hotel.rooms"
              :key="room.id"
              type="button"
              :class="{ on: room.id === selected?.id }"
              @click="pick(room.id)"
            >
              {{ room.id }}
            </button>
          </div>
          <button type="button" class="ghost-btn" :disabled="!canNext" @click="stepRoom(1)">下一间</button>
        </div>
        <div class="frame">
          <img v-if="selected?.photoUrl" :src="selected.photoUrl" :alt="selected.name" />
          <p v-else>该房间尚未上传实景图</p>
        </div>
      </section>
      <section class="hud-panel action">
        <div class="panel-title"><span>确认选择</span></div>
        <div class="pad">
          <p v-if="alreadyMine">当前已选择 {{ selected?.name }}。</p>
          <p v-else-if="occupiedByOther">{{ selected?.name }} 已被其他住客占用。</p>
          <p v-else>用实景栏切换房间，或双击三维模型中的房间，再确认本次入住选择。</p>
          <button
            class="gold-btn"
            type="button"
            :disabled="!selected || occupiedByOther || confirming"
            @click="confirm"
          >
            {{ alreadyMine ? '已选择该房间' : '确认选择该房间' }}
          </button>
        </div>
      </section>
    </aside>
  </main>
</template>

<style scoped>
.pick {
  height: 100%;
  display: grid;
  grid-template-columns: minmax(0, 1fr) 320px;
  gap: 12px;
  padding: 12px;
  min-height: 0;
}

.curtain {
  position: relative;
  min-height: 0;
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

.view-btns button {
  border: 1px solid var(--line);
  background: rgba(8, 14, 22, 0.78);
  color: var(--muted);
  padding: 6px 11px;
  cursor: pointer;
  font-size: 12px;
  border-radius: 999px;
}

.view-btns button.on {
  color: #041018;
  background: var(--cyan);
}

.rail {
  display: grid;
  grid-template-rows: minmax(0, 1fr) auto;
  gap: 10px;
  min-height: 0;
}

.photo,
.action {
  min-height: 0;
}

.switcher {
  display: grid;
  grid-template-columns: auto minmax(0, 1fr) auto;
  gap: 6px;
  align-items: center;
  padding: 8px 8px 0;
}

.ids {
  display: flex;
  flex-wrap: wrap;
  gap: 4px;
  justify-content: center;
}

.ids button {
  min-width: 42px;
  padding: 5px 7px;
  border: 1px solid var(--line);
  background: rgba(8, 14, 22, 0.78);
  color: var(--muted);
  cursor: pointer;
  font-size: 12px;
  font-family: var(--mono);
  border-radius: 6px;
}

.ids button.on {
  color: #041018;
  background: var(--cyan);
}

.switcher .ghost-btn {
  padding: 5px 8px;
  font-size: 12px;
}

.switcher .ghost-btn:disabled {
  opacity: 0.35;
  cursor: not-allowed;
}

.frame {
  height: calc(100% - 92px);
  min-height: 180px;
  display: grid;
  place-items: center;
  overflow: hidden;
  background: #070b12;
  margin: 8px;
  border-radius: 8px;
}

.frame img {
  width: 100%;
  height: 100%;
  object-fit: cover;
}

.frame p,
.pad p {
  margin: 0;
  color: var(--muted);
  padding: 16px;
}

.pad {
  padding: 16px 18px 18px;
}

.gold-btn {
  margin-top: 12px;
  width: 100%;
}

.panel-title em {
  color: var(--muted);
  font-style: normal;
}
</style>
