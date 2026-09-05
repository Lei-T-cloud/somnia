<script setup lang="ts">
import { computed, onBeforeUnmount, onMounted, ref } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { useAuthStore } from '@/stores/auth'
import { useGuestStore } from '@/stores/guest'
import { useHotelStore } from '@/stores/hotel'

const router = useRouter()
const route = useRoute()
const auth = useAuthStore()
const guests = useGuestStore()
const hotel = useHotelStore()
const opsOpen = ref(false)

const opsActive = computed(() => route.path === '/manager/twin')
const opsChildOn = computed(() => route.path === '/manager/monitor')

function toggleOps() {
  opsOpen.value = !opsOpen.value
}

onMounted(async () => {
  await guests.hydrate()
  await hotel.startSimulation()
})

onBeforeUnmount(() => {
  hotel.stopSimulation()
})

async function logout() {
  await hotel.stopSimulation()
  await auth.logout()
  router.push('/login')
}
</script>

<template>
  <div class="workbench">
    <header class="top">
      <div class="brand-mark">
        <i class="logo-orb" />
        <strong>眠栖</strong>
        <span>COMMAND</span>
      </div>
      <div class="who">
        <span class="live"><i class="status-dot" :class="{ off: !hotel.simulating }" />{{ hotel.simulating ? '仿真运行' : '仿真暂停' }}</span>
        <span class="user-chip">
          <i>{{ (auth.user?.nickname ?? '管').slice(0, 1) }}</i>
          {{ auth.user?.nickname }}
        </span>
        <button class="ghost-btn" type="button" @click="logout">退出</button>
      </div>
    </header>
    <div class="body">
      <aside class="side-nav">
        <p>酒店管理</p>
        <div class="group">
          <div class="parent" :class="{ on: opsActive, child: opsChildOn }">
            <router-link to="/manager/twin" custom v-slot="{ navigate }">
              <button type="button" class="ops" @click="navigate"><em>01</em>酒店运维</button>
            </router-link>
            <button type="button" class="exp" :aria-expanded="opsOpen" @click.stop="toggleOps">
              {{ opsOpen ? '收起' : '展开' }}
            </button>
          </div>
          <div v-if="opsOpen" class="subs">
            <router-link to="/manager/twin">实时温湿</router-link>
            <router-link to="/manager/monitor">实时监控</router-link>
          </div>
        </div>
        <router-link to="/manager/rooms"><em>02</em>房间更新</router-link>
        <router-link to="/manager/requests"><em>03</em>用户需求</router-link>
      </aside>
      <div class="main">
        <router-view />
      </div>
    </div>
  </div>
</template>

<style scoped>
.who,
.live {
  display: flex;
  align-items: center;
  gap: 12px;
}

.live {
  color: var(--muted);
  font-size: 12px;
}

.status-dot.off {
  background: var(--warn);
}

.group {
  display: flex;
  flex-direction: column;
  gap: 4px;
}

.parent {
  display: grid;
  grid-template-columns: 1fr auto;
  align-items: stretch;
  border-radius: 8px;
}

.parent.on,
.parent.child {
  background: #18181b;
}

.ops,
.exp {
  border: 0;
  background: transparent;
  color: var(--muted);
  cursor: pointer;
  font: inherit;
}

.parent.on .ops {
  color: var(--text);
}

.exp {
  padding: 0 10px;
  color: var(--cyan);
  font-size: 12px;
}

.subs a {
  padding-left: 40px;
}
</style>
