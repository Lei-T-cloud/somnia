<script setup lang="ts">
import { computed, onMounted, ref } from 'vue'
import { ElMessage } from 'element-plus'
import { apiError } from '@/api/client'
import { useHotelStore } from '@/stores/hotel'
import type { ServiceRequest } from '@/types'

const GENDER: Record<string, string> = { female: '女', male: '男', other: '不愿透露' }
const AGE: Record<string, string> = { '18-25': '18–25', '26-35': '26–35', '36-50': '36–50', '51+': '51 及以上' }
const SCENE: Record<string, string> = { business: '商务', wellness: '康养', family: '亲子', leisure: '休闲' }

const hotel = useHotelStore()
const tab = ref<'open' | 'done'>('open')
const openedId = ref<string | null>(null)
const saving = ref(false)

const visible = computed(() => hotel.serviceRequests.filter((item) => (tab.value === 'done' ? item.completed : !item.completed)))
const opened = computed(() => visible.value.find((item) => item.roomId === openedId.value) ?? null)

onMounted(async () => {
  await hotel.fetchServiceRequests()
})

function switchTab(next: 'open' | 'done') {
  tab.value = next
  openedId.value = null
}

function toggleRoom(roomId: string) {
  openedId.value = openedId.value === roomId ? null : roomId
}

function label(map: Record<string, string>, value: string | null) {
  if (!value) return '未填写'
  return map[value] ?? value
}

async function mark(row: ServiceRequest, completed: boolean) {
  saving.value = true
  try {
    await hotel.setRequestCompleted(row.roomId, completed)
    ElMessage.success(completed ? `${row.roomName} 已标记完成` : `${row.roomName} 已退回未完成`)
    openedId.value = completed ? null : row.roomId
    if (completed) tab.value = 'done'
    else tab.value = 'open'
  } catch (error) {
    ElMessage.error(apiError(error, '无法更新服务状态'))
  } finally {
    saving.value = false
  }
}
</script>

<template>
  <main class="requests">
    <section class="hud-panel intro">
      <div class="panel-title"><span>用户需求</span><em>按房间跟进</em></div>
      <p>先选择未完成或已完成服务，点开房间后查看住客信息与具体需求。</p>
      <div class="tabs">
        <button type="button" :class="{ on: tab === 'open' }" @click="switchTab('open')">
          未完成服务 · {{ hotel.serviceRequests.filter((item) => !item.completed).length }}
        </button>
        <button type="button" :class="{ on: tab === 'done' }" @click="switchTab('done')">
          已完成服务 · {{ hotel.serviceRequests.filter((item) => item.completed).length }}
        </button>
      </div>
    </section>

    <p v-if="!visible.length" class="empty">
      {{ tab === 'open' ? '暂无未完成服务的房间。' : '暂无已完成服务的房间。' }}
    </p>

    <div v-else class="grid">
      <article v-for="row in visible" :key="row.roomId" class="hud-panel room" :class="{ on: openedId === row.roomId }">
        <button type="button" class="room-btn" @click="toggleRoom(row.roomId)">
          <strong>{{ row.roomName }}</strong>
          <em>{{ row.floor }}F · {{ row.services.length }} 项服务</em>
        </button>
      </article>
    </div>

    <section v-if="opened" class="hud-panel detail">
      <div class="panel-title">
        <span>{{ opened.roomName }} · 住客与需求</span>
        <em>{{ tab === 'done' ? '已完成' : '未完成' }}</em>
      </div>
      <div class="pad">
        <div class="who">
          <img v-if="opened.photoUrl" :src="opened.photoUrl" :alt="opened.roomName" />
          <div>
            <h3>{{ opened.nickname }}</h3>
            <small>{{ opened.guestEmail }}</small>
            <p>
              {{ label(GENDER, opened.gender) }} · {{ label(AGE, opened.ageGroup) }} ·
              {{ label(SCENE, opened.stayScene) }}
            </p>
            <p v-if="opened.fragrance">香氛偏好：{{ opened.fragrance }}</p>
            <p v-if="opened.bedtimeHabit">睡前习惯：{{ opened.bedtimeHabit }}</p>
          </div>
        </div>
        <h4>已选酒店服务</h4>
        <ul>
          <li v-for="item in opened.services" :key="item.id">
            <b>{{ item.name }}</b>
            <span>{{ item.group }} · {{ item.description }}</span>
          </li>
        </ul>
        <button
          v-if="tab === 'open'"
          class="gold-btn"
          type="button"
          :disabled="saving"
          @click="mark(opened, true)"
        >
          标记为已完成
        </button>
        <button v-else class="ghost-btn" type="button" :disabled="saving" @click="mark(opened, false)">
          退回未完成
        </button>
      </div>
    </section>
  </main>
</template>

<style scoped>
.requests {
  height: 100%;
  overflow: auto;
  padding: 16px;
  display: grid;
  gap: 14px;
  align-content: start;
}

.intro p,
.empty {
  margin: 0;
  padding: 16px 18px 8px;
  color: var(--muted);
}

.tabs {
  display: flex;
  gap: 8px;
  padding: 0 16px 16px;
}

.tabs button {
  flex: 1;
  padding: 11px 12px;
  border: 1px solid var(--line);
  background: rgba(8, 14, 22, 0.7);
  color: var(--muted);
  cursor: pointer;
  letter-spacing: 0.06em;
  border-radius: var(--radius-sm);
}

.tabs button.on {
  color: #041018;
  background: linear-gradient(180deg, #7adfef, var(--cyan));
}

.grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(168px, 1fr));
  gap: 12px;
}

.room.on {
  box-shadow: 0 0 20px rgba(90, 210, 255, 0.16);
  border-color: var(--cyan);
}

.room-btn {
  width: 100%;
  text-align: left;
  padding: 16px;
  border: 0;
  background: transparent;
  color: inherit;
  cursor: pointer;
}

.room-btn strong {
  display: block;
  font-size: 18px;
}

.room-btn em {
  display: block;
  margin-top: 6px;
  color: var(--muted);
  font-style: normal;
  font-size: 12px;
}

.pad {
  padding: 14px 16px 18px;
}

.who {
  display: grid;
  grid-template-columns: 140px minmax(0, 1fr);
  gap: 14px;
  align-items: start;
}

.who img {
  width: 140px;
  height: 92px;
  object-fit: cover;
  border-radius: 8px;
}

h3,
h4 {
  margin: 0 0 6px;
}

h4 {
  margin-top: 16px;
}

small,
p,
li span {
  color: var(--muted);
}

small {
  font-family: var(--mono);
}

ul {
  margin: 8px 0 16px;
  padding: 0;
  list-style: none;
  display: grid;
  gap: 10px;
}

li {
  display: grid;
  gap: 2px;
  padding-bottom: 10px;
  border-bottom: 1px solid var(--line);
}

.panel-title em {
  color: var(--muted);
  font-style: normal;
}

@media (max-width: 720px) {
  .who {
    grid-template-columns: 1fr;
  }
}
</style>
