<script setup lang="ts">
import { reactive, ref } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
import { useAuthStore } from '@/stores/auth'
import type { UserRole } from '@/types'

const router = useRouter()
const auth = useAuthStore()

const role = ref<UserRole | null>(null)
const mode = ref<'login' | 'register'>('login')
const loading = ref(false)
const form = reactive({
  email: '',
  password: '',
  nickname: '',
})

function chooseRole(next: UserRole) {
  role.value = next
  mode.value = 'login'
  form.email = next === 'guest' ? 'guest@somnia.demo' : 'manager@somnia.demo'
  form.password = 'somnia123'
  form.nickname = ''
}

function homeOf(next: UserRole) {
  return next === 'manager' ? '/manager/twin' : '/guest/preference'
}

async function submit() {
  if (!role.value) return
  loading.value = true
  const error =
    mode.value === 'register'
      ? await auth.register(form.email, form.password, form.nickname)
      : await auth.login(form.email, form.password, role.value)
  loading.value = false
  if (error) {
    ElMessage.error(error)
    return
  }
  ElMessage.success(role.value === 'manager' ? '已进入酒店管理端' : '欢迎回来，可以完善睡眠偏好')
  router.push(homeOf(role.value))
}
</script>

<template>
  <main class="login">
    <section class="showcase">
      <div class="brand-mark">
        <i class="logo-orb" />
        <strong>眠栖 Somnia</strong>
      </div>
      <div class="copy">
        <p class="eyebrow">睡眠经济 · 可配置客房</p>
        <h1>把客房变成可配置的睡眠环境产品</h1>
        <p>住客提交睡眠偏好，规则引擎生成睡眠场景；酒店在三维数字孪生中感知环境并执行调控。</p>
      </div>
      <ol>
        <li><b>01</b>偏好采集</li>
        <li><b>02</b>场景决策</li>
        <li><b>03</b>环境执行</li>
        <li><b>04</b>状态反馈</li>
      </ol>
      <footer>
        <span>演示平台 · 环境数据来自仿真器</span>
      </footer>
    </section>

    <section class="access">
      <div class="card">
        <header>
          <h2>{{ role ? (role === 'guest' ? '住客登录' : '管理员登录') : '选择入口' }}</h2>
          <p>{{ role ? '演示账号已预填，密码均为 somnia123' : '同一平台，双角色分流' }}</p>
        </header>

        <div class="gate" v-if="!role">
          <button class="role-card" type="button" @click="chooseRole('guest')">
            <strong>我是住客</strong>
            <span>填写睡眠偏好、选择客房并提交酒店服务</span>
          </button>
          <button class="role-card" type="button" @click="chooseRole('manager')">
            <strong>酒店管理人员</strong>
            <span>进入三维数字孪生，查看房间并一键适配</span>
          </button>
          <ul class="accounts">
            <li><b>guest@somnia.demo</b><em>住客</em></li>
            <li><b>manager@somnia.demo</b><em>管理</em></li>
          </ul>
        </div>

        <div class="form" v-else>
          <button class="back" type="button" @click="role = null">返回选择入口</button>
          <el-form label-position="top" @submit.prevent="submit">
            <el-form-item label="邮箱">
              <el-input v-model="form.email" autocomplete="username" />
            </el-form-item>
            <el-form-item v-if="mode === 'register'" label="昵称">
              <el-input v-model="form.nickname" />
            </el-form-item>
            <el-form-item label="密码">
              <el-input v-model="form.password" type="password" show-password autocomplete="current-password" />
            </el-form-item>
            <div class="actions">
              <button class="gold-btn" type="submit" :disabled="loading">
                {{ mode === 'register' ? '注册并进入' : '进入工作台' }}
              </button>
              <button
                v-if="role === 'guest'"
                class="ghost-btn"
                type="button"
                @click="mode = mode === 'login' ? 'register' : 'login'"
              >
                {{ mode === 'login' ? '没有账号？注册住客' : '已有账号？去登录' }}
              </button>
            </div>
          </el-form>
        </div>
      </div>
    </section>
  </main>
</template>

<style scoped>
.login {
  min-height: 100vh;
  display: grid;
  grid-template-columns: 1.05fr 0.95fr;
  background:
    linear-gradient(90deg, rgba(9, 9, 11, 0.72) 0%, rgba(9, 9, 11, 0.38) 48%, rgba(9, 9, 11, 0.62) 100%),
    url("/login-bg.jpg") center / cover no-repeat;
}

.showcase {
  padding: 36px 48px 32px;
  display: flex;
  flex-direction: column;
  border-right: 1px solid transparent;
  background: transparent;
}

.copy {
  margin: auto 0;
  max-width: 520px;
}

.eyebrow {
  margin: 0 0 12px;
  color: var(--cyan);
  font-size: 12px;
  letter-spacing: 0.08em;
}

h1 {
  margin: 0 0 14px;
  font-size: clamp(32px, 4vw, 46px);
  line-height: 1.15;
  letter-spacing: -0.035em;
  font-weight: 650;
}

.copy p:last-of-type {
  margin: 0;
  color: var(--muted);
  font-size: 15px;
}

ol {
  list-style: none;
  margin: 0 0 28px;
  padding: 0;
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 10px;
}

ol li {
  display: flex;
  gap: 10px;
  align-items: center;
  color: var(--muted);
  font-size: 14px;
}

ol b {
  color: var(--text);
  font-size: 12px;
  font-variant-numeric: tabular-nums;
}

footer {
  color: #71717a;
  font-size: 12px;
}

.access {
  display: grid;
  place-items: center;
  padding: 32px 24px;
}

.card {
  width: min(440px, 100%);
  padding: 28px;
  border: 1px solid rgba(255, 255, 255, 0.12);
  border-radius: 16px;
  background: rgba(17, 17, 19, 0.78);
  backdrop-filter: blur(16px);
  box-shadow: var(--shadow);
}

.card header h2 {
  margin: 0 0 6px;
  font-size: 22px;
  letter-spacing: -0.03em;
}

.card header p {
  margin: 0 0 22px;
  color: var(--muted);
  font-size: 13px;
}

.gate,
.form {
  display: grid;
  gap: 10px;
}

.role-card {
  text-align: left;
  padding: 16px;
  border-radius: 10px;
  border: 1px solid var(--line);
  background: #09090b;
  color: var(--text);
  cursor: pointer;
}

.role-card:hover {
  border-color: var(--line-strong);
  background: var(--bg-hover);
}

.role-card strong {
  display: block;
  margin-bottom: 6px;
  font-size: 15px;
}

.role-card span {
  color: var(--muted);
  font-size: 13px;
}

.accounts {
  list-style: none;
  margin: 8px 0 0;
  padding: 0;
  display: grid;
  gap: 8px;
}

.accounts li {
  display: flex;
  justify-content: space-between;
  padding: 10px 12px;
  border: 1px solid var(--line);
  border-radius: 8px;
  font-size: 12px;
  color: var(--muted);
}

.accounts em {
  font-style: normal;
  color: var(--cyan);
}

.back {
  justify-self: start;
  border: 0;
  background: none;
  color: var(--muted);
  padding: 0 0 8px;
  cursor: pointer;
}

.back:hover {
  color: var(--text);
}

.actions {
  display: flex;
  gap: 10px;
  flex-wrap: wrap;
}

.gold-btn {
  min-width: 120px;
}

@media (max-width: 980px) {
  .login {
    grid-template-columns: 1fr;
  }

  .showcase {
    min-height: auto;
    border-right: 0;
    border-bottom: 1px solid var(--line);
  }
}
</style>
