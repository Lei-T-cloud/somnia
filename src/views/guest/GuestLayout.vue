<script setup lang="ts">
import { onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { useAuthStore } from '@/stores/auth'
import { useGuestStore } from '@/stores/guest'

const router = useRouter()
const auth = useAuthStore()
const guests = useGuestStore()

onMounted(async () => {
  if (!auth.user) return
  await guests.hydrate()
  await guests.ensureGuest(auth.user.email, auth.user.nickname)
})

async function logout() {
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
        <span>GUEST</span>
      </div>
      <div class="who">
        <span class="user-chip">
          <i>{{ (auth.user?.nickname ?? '住').slice(0, 1) }}</i>
          {{ auth.user?.nickname }}
        </span>
        <button class="ghost-btn" type="button" @click="logout">退出</button>
      </div>
    </header>
    <div class="body">
      <aside class="side-nav">
        <p>住客工作台</p>
        <router-link to="/guest/preference"><em>01</em>用户偏好</router-link>
        <router-link to="/guest/rooms"><em>02</em>房间选择</router-link>
        <router-link to="/guest/services"><em>03</em>酒店服务</router-link>
      </aside>
      <div class="main">
        <router-view />
      </div>
    </div>
  </div>
</template>

<style scoped>
.who {
  display: flex;
  align-items: center;
  gap: 12px;
}
</style>
