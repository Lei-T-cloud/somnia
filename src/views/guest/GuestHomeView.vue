<script setup lang="ts">
import { computed } from 'vue'
import { useAuthStore } from '@/stores/auth'
import { useGuestStore } from '@/stores/guest'

const auth = useAuthStore()
const guests = useGuestStore()

const portrait = computed(() => guests.current?.portrait ?? null)
</script>

<template>
  <main class="home">
    <aside class="hud-panel">
      <div class="panel-title"><span>睡眠画像</span></div>
      <div class="pad">
        <template v-if="portrait">
          <h3>{{ portrait.sceneName }}</h3>
          <p>{{ portrait.sceneSummary }}</p>
          <strong>{{ portrait.settings.targetTemp }}°C / {{ portrait.settings.targetHumidity }}%</strong>
        </template>
        <p v-else>尚未生成画像。完成后，管理端可读取并一键应用。</p>
      </div>
    </aside>

    <section class="hud-panel">
      <div class="panel-title"><span>住客工作台</span><em>偏好采集节点</em></div>
      <div class="pad">
        <p class="eyebrow">偏好采集 → 场景决策 → 环境执行 → 状态反馈</p>
        <h1>{{ auth.user?.nickname }}，今晚按你的节律睡</h1>
        <p>先形成睡眠画像，酒店数字孪生才能把偏好变成可执行的房间设定。</p>
        <router-link class="gold-btn link-btn" to="/guest/profile">
          {{ portrait ? '查看或更新睡眠画像' : '填写睡眠偏好' }}
        </router-link>
      </div>
    </section>

    <aside class="hud-panel">
      <div class="panel-title"><span>闭环说明</span></div>
      <ol>
        <li>提交睡眠偏好</li>
        <li>规则引擎生成场景</li>
        <li>管理端三维可见</li>
        <li>仿真器逼近目标值</li>
      </ol>
    </aside>
  </main>
</template>

<style scoped>
.home {
  display: grid;
  grid-template-columns: 260px minmax(0, 1fr) 240px;
  gap: 12px;
  padding: 16px;
  min-height: calc(100vh - 52px);
}

.pad,
ol {
  padding: 18px 20px 22px;
}

.eyebrow {
  color: var(--cyan);
  letter-spacing: 0.1em;
  font-size: 12px;
  font-family: var(--mono);
}

h1 {
  font-size: clamp(26px, 3.4vw, 40px);
  margin: 8px 0 12px;
}

p,
ol {
  color: var(--muted);
}

strong {
  display: block;
  margin-top: 12px;
  font-family: var(--mono);
  font-size: 22px;
  color: var(--cyan);
}

.link-btn {
  display: inline-block;
  margin-top: 18px;
  text-decoration: none;
}

.panel-title em {
  color: var(--muted);
  font-style: normal;
}

@media (max-width: 980px) {
  .home {
    grid-template-columns: 1fr;
  }
}
</style>
