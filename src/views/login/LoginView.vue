<script setup lang="ts">
import { onMounted, reactive, ref } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
import { api } from '@/api/client'
import { useAuthStore } from '@/stores/auth'
import type { UserRole } from '@/types'

const router = useRouter()
const auth = useAuthStore()

const mode = ref<'login' | 'register'>('login')
const registerRole = ref<UserRole>('guest')
const loading = ref(false)
const sending = ref(false)
const countdown = ref(0)
const captchaImage = ref('')
const captchaId = ref('')
const apiReady = ref(true)
const form = reactive({
  email: '',
  password: '',
  confirm: '',
  nickname: '',
  captcha: '',
  emailCode: '',
})

onMounted(async () => {
  try {
    await api.get('/health')
    apiReady.value = true
    await refreshCaptcha()
  } catch {
    apiReady.value = false
  }
})

async function refreshCaptcha() {
  try {
    const data = await auth.fetchCaptcha()
    captchaId.value = data.captchaId
    captchaImage.value = data.image
    form.captcha = ''
  } catch {
    ElMessage.error('验证码加载失败')
  }
}

function resetForm() {
  form.email = ''
  form.password = ''
  form.confirm = ''
  form.nickname = ''
  form.captcha = ''
  form.emailCode = ''
}

function switchMode(next: 'login' | 'register') {
  mode.value = next
  resetForm()
  if (next === 'login') refreshCaptcha()
}

async function sendCode() {
  const email = form.email.trim().toLowerCase()
  if (!email) {
    ElMessage.error('请先填写邮箱')
    return
  }
  sending.value = true
  const error = await auth.sendEmailCode(email, 'register')
  sending.value = false
  if (error) {
    ElMessage.error(error)
    return
  }
  ElMessage.success('验证码已发送，请查收邮箱')
  countdown.value = 60
  const timer = window.setInterval(() => {
    countdown.value -= 1
    if (countdown.value <= 0) window.clearInterval(timer)
  }, 1000)
}

async function submit() {
  const email = form.email.trim().toLowerCase()
  const password = form.password
  if (!email || !password) {
    ElMessage.error('请填写邮箱和密码')
    return
  }
  if (mode.value === 'login' && !form.captcha.trim()) {
    ElMessage.error('请填写验证码')
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
    if (!form.emailCode.trim()) {
      ElMessage.error('请填写邮箱验证码')
      return
    }
  }

  loading.value = true
  const result =
    mode.value === 'register'
      ? await auth.register(email, password, form.nickname.trim(), registerRole.value, form.emailCode.trim())
      : await auth.login(email, password, captchaId.value, form.captcha.trim())
  loading.value = false
  if (result === 'pending') {
    ElMessage.success('已提交，等待同意后才能进入数据后台')
    switchMode('login')
    return
  }
  if (result) {
    ElMessage.error(result)
    if (mode.value === 'login') refreshCaptcha()
    return
  }
  const next = auth.enterHome()
  if (next) router.push(next)
}
</script>

<template>
  <main class="login">
    <section class="access">
      <div class="card">
        <div class="brand-mark">
          <i class="logo-orb" />
          <strong>眠栖 Somnia</strong>
        </div>
        <header>
          <h2>{{ mode === 'login' ? '登录' : '注册' }}</h2>
        </header>
        <p v-if="!apiReady" class="offline">当前网页没有后台服务，无法发送验证码。请使用桌面版完成注册和登录。</p>

        <div v-if="mode === 'register'" class="roles">
          <button type="button" :class="{ on: registerRole === 'guest' }" @click="registerRole = 'guest'">住客</button>
          <button type="button" :class="{ on: registerRole === 'manager' }" @click="registerRole = 'manager'">酒店员工</button>
          <button type="button" :class="{ on: registerRole === 'backend' }" @click="registerRole = 'backend'">数据后台</button>
        </div>

        <el-form label-position="top" @submit.prevent="submit">
          <el-form-item v-if="mode === 'register'" label="姓名">
            <el-input v-model="form.nickname" autocomplete="name" />
          </el-form-item>
          <el-form-item label="邮箱">
            <el-input v-model="form.email" autocomplete="username" placeholder="请输入常用邮箱" />
          </el-form-item>
          <el-form-item label="密码">
            <el-input
              v-model="form.password"
              type="password"
              show-password
              :autocomplete="mode === 'register' ? 'new-password' : 'current-password'"
            />
          </el-form-item>
          <el-form-item v-if="mode === 'register'" label="确认密码">
            <el-input v-model="form.confirm" type="password" show-password autocomplete="new-password" />
          </el-form-item>
          <el-form-item v-if="mode === 'register'" label="邮箱验证码">
            <div class="code-row">
              <el-input v-model="form.emailCode" maxlength="6" />
              <button class="ghost-btn" type="button" :disabled="!apiReady || sending || countdown > 0" @click="sendCode">
                {{ countdown > 0 ? `${countdown}s` : '发送验证码' }}
              </button>
            </div>
          </el-form-item>
          <el-form-item v-else label="验证码">
            <div class="code-row">
              <el-input v-model="form.captcha" maxlength="4" />
              <button class="captcha" type="button" @click="refreshCaptcha">
                <img v-if="captchaImage" :src="captchaImage" alt="验证码" />
              </button>
            </div>
          </el-form-item>
          <div class="actions">
            <button class="gold-btn" type="submit" :disabled="loading || !apiReady">
              {{ mode === 'register' ? (registerRole === 'backend' ? '提交申请' : '注册') : '登录' }}
            </button>
            <button class="ghost-btn" type="button" @click="switchMode(mode === 'login' ? 'register' : 'login')">
              {{ mode === 'login' ? '注册账号' : '返回登录' }}
            </button>
          </div>
        </el-form>
      </div>
    </section>
  </main>
</template>

<style scoped>
.login {
  min-height: 100vh;
  display: grid;
  place-items: center;
  background:
    linear-gradient(90deg, rgba(9, 9, 11, 0.66) 0%, rgba(9, 9, 11, 0.5) 100%),
    url("/login-bg.jpg") center / cover no-repeat;
}

.card {
  width: min(420px, calc(100vw - 32px));
  padding: 28px;
  border: 1px solid rgba(255, 255, 255, 0.12);
  border-radius: 16px;
  background: rgba(17, 17, 19, 0.82);
  backdrop-filter: blur(16px);
  box-shadow: var(--shadow);
}

.brand-mark {
  margin-bottom: 18px;
}

.card header h2 {
  margin: 0 0 18px;
  font-size: 22px;
  letter-spacing: -0.03em;
}

.roles {
  display: grid;
  grid-template-columns: 1fr 1fr 1fr;
  gap: 8px;
  margin-bottom: 16px;
}

.roles button {
  border: 1px solid var(--line);
  background: #09090b;
  color: var(--muted);
  border-radius: 10px;
  padding: 10px 8px;
  cursor: pointer;
}

.roles button.on {
  border-color: var(--line-strong);
  color: var(--text);
  background: var(--bg-hover);
}

.code-row {
  display: grid;
  grid-template-columns: 1fr auto;
  gap: 8px;
  width: 100%;
}

.captcha {
  width: 140px;
  height: 40px;
  padding: 0;
  border: 1px solid var(--line);
  border-radius: 8px;
  background: #09090b;
  cursor: pointer;
  overflow: hidden;
}

.captcha img {
  width: 100%;
  height: 100%;
  object-fit: cover;
  display: block;
}

.actions {
  display: flex;
  gap: 10px;
  flex-wrap: wrap;
}

.gold-btn {
  min-width: 120px;
}

.offline {
  margin: 0 0 16px;
  color: var(--muted);
  font-size: 13px;
}
</style>
