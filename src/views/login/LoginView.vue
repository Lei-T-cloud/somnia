<script setup lang="ts">
import { reactive, ref } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
import { useAuthStore } from '@/stores/auth'
import type { UserRole } from '@/types'

const router = useRouter()
const auth = useAuthStore()

const mode = ref<'login' | 'register'>('login')
const registerRole = ref<UserRole>('guest')
const loading = ref(false)
const form = reactive({
  email: '',
  password: '',
  confirm: '',
  nickname: '',
  inviteCode: '',
})

function homeOf(role: UserRole) {
  return role === 'manager' ? '/manager/twin' : '/guest/preference'
}

function resetForm() {
  form.email = ''
  form.password = ''
  form.confirm = ''
  form.nickname = ''
  form.inviteCode = ''
}

function switchMode(next: 'login' | 'register') {
  mode.value = next
  resetForm()
}

async function submit() {
  const email = form.email.trim().toLowerCase()
  const password = form.password
  if (!email || !password) {
    ElMessage.error('请填写邮箱和密码')
    return
  }
  if (mode.value === 'register') {
    if (!form.nickname.trim()) {
      ElMessage.error('请填写姓名')
      return
    }
    if (password.length < 8) {
      ElMessage.error('密码至少 8 位')
      return
    }
    if (password !== form.confirm) {
      ElMessage.error('两次输入的密码不一致')
      return
    }
  }

  loading.value = true
  const error =
    mode.value === 'register'
      ? await auth.register(email, password, form.nickname.trim(), registerRole.value, form.inviteCode.trim())
      : await auth.login(email, password)
  loading.value = false
  if (error) {
    ElMessage.error(error)
    return
  }
  const role = auth.role
  if (!role) {
    ElMessage.error('登录状态异常，请重试')
    return
  }
  ElMessage.success(role === 'manager' ? '欢迎回来' : '登录成功')
  router.push(homeOf(role))
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
        <span>环境数据来自环境仿真</span>
      </footer>
    </section>

    <section class="access">
      <div class="card">
        <header>
          <h2>{{ mode === 'login' ? '登录' : '创建账号' }}</h2>
          <p>{{ mode === 'login' ? '使用邮箱和密码进入眠栖' : '选择身份后填写资料，即可开始使用' }}</p>
        </header>

        <div v-if="mode === 'register'" class="roles">
          <button type="button" :class="{ on: registerRole === 'guest' }" @click="registerRole = 'guest'">住客</button>
          <button type="button" :class="{ on: registerRole === 'manager' }" @click="registerRole = 'manager'">酒店员工</button>
        </div>

        <el-form label-position="top" @submit.prevent="submit">
          <el-form-item v-if="mode === 'register'" label="姓名">
            <el-input v-model="form.nickname" autocomplete="name" placeholder="怎么称呼您" />
          </el-form-item>
          <el-form-item label="邮箱">
            <el-input v-model="form.email" autocomplete="username" placeholder="name@example.com" />
          </el-form-item>
          <el-form-item label="密码">
            <el-input
              v-model="form.password"
              type="password"
              show-password
              :autocomplete="mode === 'register' ? 'new-password' : 'current-password'"
              :placeholder="mode === 'register' ? '至少 8 位' : '请输入密码'"
            />
          </el-form-item>
          <el-form-item v-if="mode === 'register'" label="确认密码">
            <el-input v-model="form.confirm" type="password" show-password autocomplete="new-password" placeholder="再输入一次密码" />
          </el-form-item>
          <el-form-item v-if="mode === 'register' && registerRole === 'manager'" label="员工邀请码">
            <el-input v-model="form.inviteCode" placeholder="首位员工无需填写，之后加入请向管理员索取" />
          </el-form-item>
          <div class="actions">
            <button class="gold-btn" type="submit" :disabled="loading">
              {{ mode === 'register' ? '注册并进入' : '登录' }}
            </button>
            <button class="ghost-btn" type="button" @click="switchMode(mode === 'login' ? 'register' : 'login')">
              {{ mode === 'login' ? '没有账号？注册' : '已有账号？去登录' }}
            </button>
          </div>
        </el-form>
        <p class="hint">忘记密码时，请联系酒店工作人员在数据后台重置。</p>
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

.roles {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 8px;
  margin-bottom: 16px;
}

.roles button {
  border: 1px solid var(--line);
  background: #09090b;
  color: var(--muted);
  border-radius: 10px;
  padding: 10px 12px;
  cursor: pointer;
}

.roles button.on {
  border-color: var(--line-strong);
  color: var(--text);
  background: var(--bg-hover);
}

.actions {
  display: flex;
  gap: 10px;
  flex-wrap: wrap;
}

.gold-btn {
  min-width: 120px;
}

.hint {
  margin: 16px 0 0;
  color: #71717a;
  font-size: 12px;
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
