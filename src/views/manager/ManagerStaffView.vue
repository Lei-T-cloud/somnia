<script setup lang="ts">
import { computed, onMounted, ref } from 'vue'
import { ElMessage } from 'element-plus'
import { api, apiError } from '@/api/client'
import type { StaffAccount } from '@/types'

const STATUS: Record<StaffAccount['status'], string> = {
  pending: '待审核',
  active: '已通过',
  rejected: '已拒绝',
}

const rows = ref<StaffAccount[]>([])
const tab = ref<'pending' | 'active' | 'rejected'>('pending')
const saving = ref('')

const visible = computed(() => rows.value.filter((item) => item.status === tab.value && !item.isOwner))

onMounted(load)

async function load() {
  const { data } = await api.get<StaffAccount[]>('/hotel/staff')
  rows.value = data
}

async function review(row: StaffAccount, approved: boolean) {
  saving.value = row.email
  try {
    const { data } = await api.post<StaffAccount>(`/hotel/staff/${encodeURIComponent(row.email)}/review`, { approved })
    const index = rows.value.findIndex((item) => item.email === row.email)
    if (index >= 0) rows.value[index] = data
    ElMessage.success(approved ? `已同意 ${row.nickname} 进入管理端` : `已拒绝 ${row.nickname}`)
    if (approved) tab.value = 'active'
    else tab.value = 'rejected'
  } catch (error) {
    ElMessage.error(apiError(error, '无法更新审核状态'))
  } finally {
    saving.value = ''
  }
}
</script>

<template>
  <main class="staff">
    <section class="hud-panel intro">
      <div class="panel-title"><span>员工审核</span><em>主管理员同意后才能进入</em></div>
      <p>酒店员工自行注册后会出现在这里。未通过前不能登录管理端，也不能进入数据后台。</p>
      <div class="tabs">
        <button type="button" :class="{ on: tab === 'pending' }" @click="tab = 'pending'">
          待审核 · {{ rows.filter((item) => item.status === 'pending').length }}
        </button>
        <button type="button" :class="{ on: tab === 'active' }" @click="tab = 'active'">
          已通过 · {{ rows.filter((item) => item.status === 'active' && !item.isOwner).length }}
        </button>
        <button type="button" :class="{ on: tab === 'rejected' }" @click="tab = 'rejected'">
          已拒绝 · {{ rows.filter((item) => item.status === 'rejected').length }}
        </button>
      </div>
    </section>

    <p v-if="!visible.length" class="empty">
      {{ tab === 'pending' ? '暂无待审核员工。' : tab === 'active' ? '暂无已通过的员工。' : '暂无已拒绝的申请。' }}
    </p>

    <div v-else class="list">
      <article v-for="row in visible" :key="row.email" class="hud-panel card">
        <div>
          <strong>{{ row.nickname }}</strong>
          <em>{{ row.email }}</em>
        </div>
        <span>{{ STATUS[row.status] }}</span>
        <div class="actions">
          <button class="gold-btn" type="button" :disabled="saving === row.email" @click="review(row, true)">同意</button>
          <button class="ghost-btn" type="button" :disabled="saving === row.email" @click="review(row, false)">拒绝</button>
        </div>
      </article>
    </div>
  </main>
</template>

<style scoped>
.staff {
  padding: 20px 24px 32px;
  display: grid;
  gap: 16px;
}

.intro p {
  margin: 0 0 14px;
  color: var(--muted);
  font-size: 13px;
}

.tabs {
  display: flex;
  gap: 8px;
  flex-wrap: wrap;
}

.tabs button {
  border: 1px solid var(--line);
  background: #09090b;
  color: var(--muted);
  border-radius: 8px;
  padding: 8px 12px;
  cursor: pointer;
}

.tabs button.on {
  color: var(--text);
  border-color: var(--line-strong);
  background: var(--bg-hover);
}

.empty {
  margin: 0;
  color: var(--muted);
}

.list {
  display: grid;
  gap: 10px;
}

.card {
  display: grid;
  grid-template-columns: 1fr auto auto;
  gap: 16px;
  align-items: center;
  padding: 16px 18px;
}

.card strong {
  display: block;
}

.card em,
.card span {
  color: var(--muted);
  font-style: normal;
  font-size: 13px;
}

.actions {
  display: flex;
  gap: 8px;
}
</style>
