<script setup lang="ts">
import { onMounted, reactive, ref } from 'vue'
import { ElMessage } from 'element-plus'
import { api, apiError } from '@/api/client'

const loading = ref(false)
const form = reactive({
  user: '',
  password: '',
  host: '',
  port: 465,
  useSsl: true,
  hasPassword: false,
})

onMounted(load)

async function load() {
  const { data } = await api.get('/hotel/mail')
  form.user = data.user || ''
  form.host = data.host || 'smtp.qq.com'
  form.port = data.port || 465
  form.useSsl = data.useSsl
  form.hasPassword = data.hasPassword
}

async function save(test = false) {
  loading.value = true
  try {
    const { data } = await api.put('/hotel/mail', {
      user: form.user,
      password: form.password,
      host: form.host,
      port: form.port,
      useSsl: form.useSsl,
      test,
    })
    form.hasPassword = data.hasPassword
    form.password = ''
    ElMessage.success(test ? '测试邮件已发送，请查收' : '发信设置已保存')
  } catch (error) {
    ElMessage.error(apiError(error, '无法保存发信设置'))
  } finally {
    loading.value = false
  }
}
</script>

<template>
  <main class="mail">
    <section class="hud-panel">
      <div class="panel-title"><span>发信设置</span></div>
      <p>注册验证码由这只邮箱发出。QQ 邮箱请到邮箱设置里开启 SMTP，并填写授权码，不要填登录密码。</p>
      <el-form label-position="top" @submit.prevent="save(false)">
        <el-form-item label="发信邮箱">
          <el-input v-model="form.user" placeholder="name@qq.com" />
        </el-form-item>
        <el-form-item :label="form.hasPassword ? '授权码（不填则保持原值）' : 'SMTP 授权码'">
          <el-input v-model="form.password" type="password" show-password />
        </el-form-item>
        <el-form-item label="服务器">
          <el-input v-model="form.host" />
        </el-form-item>
        <el-form-item label="端口">
          <el-input-number v-model="form.port" :min="1" :max="65535" />
        </el-form-item>
        <div class="actions">
          <button class="gold-btn" type="submit" :disabled="loading">保存</button>
          <button class="ghost-btn" type="button" :disabled="loading" @click="save(true)">保存并试发</button>
        </div>
      </el-form>
    </section>
  </main>
</template>

<style scoped>
.mail {
  padding: 20px 24px;
}

p {
  color: var(--muted);
  font-size: 13px;
}

.actions {
  display: flex;
  gap: 10px;
}
</style>
