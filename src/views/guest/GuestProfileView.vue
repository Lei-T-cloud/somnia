<script setup lang="ts">
import { computed, ref } from 'vue'
import { ElMessage } from 'element-plus'
import PreferenceForm from '@/components/guest/PreferenceForm.vue'
import { useAuthStore } from '@/stores/auth'
import { useGuestStore } from '@/stores/guest'
import type { SleepPreference } from '@/types'

const auth = useAuthStore()
const guests = useGuestStore()
const formComp = ref<InstanceType<typeof PreferenceForm> | null>(null)
const saving = ref(false)

const current = computed(() => guests.current)
const uploaded = computed(() => Boolean(current.value?.preference))

async function confirm() {
  try {
    await formComp.value?.validate()
  } catch {
    return
  }
  const value = formComp.value?.form as SleepPreference | undefined
  if (!value || !auth.user) return
  saving.value = true
  try {
    await guests.savePreference(auth.user.email, { ...value, issues: [...value.issues] })
    ElMessage.success('偏好已确认并上传')
  } finally {
    saving.value = false
  }
}
</script>

<template>
  <main class="profile">
    <section class="hud-panel card">
      <div class="panel-title">
        <span>用户偏好</span>
        <em :class="{ ready: uploaded }">{{ uploaded ? '已上传后端' : '待确认' }}</em>
      </div>
      <div class="pad">
        <p class="page-lead">填写个人信息与睡眠偏好，确认后上传酒店后端。管理端可据此适配客房环境。</p>
        <PreferenceForm
          ref="formComp"
          :model="current?.preference ?? null"
          :nickname-fallback="auth.user?.nickname ?? ''"
        />
        <div class="foot">
          <button class="gold-btn" type="button" :disabled="saving" @click="confirm">
            {{ uploaded ? '更新并上传偏好' : '确认偏好并上传' }}
          </button>
        </div>
      </div>
    </section>
  </main>
</template>

<style scoped>
.profile {
  height: 100%;
  overflow: auto;
  padding: 20px;
}

.pad {
  padding: 22px 24px 28px;
}

.foot {
  margin-top: 8px;
}

.panel-title em {
  color: var(--warn);
  font-style: normal;
}

.panel-title em.ready {
  color: var(--green);
}
</style>
