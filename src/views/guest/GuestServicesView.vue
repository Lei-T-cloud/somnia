<script setup lang="ts">
import { computed, onMounted, ref } from 'vue'
import { ElMessage } from 'element-plus'
import { useAuthStore } from '@/stores/auth'
import { useGuestStore } from '@/stores/guest'
import type { HotelService } from '@/types'

const auth = useAuthStore()
const guests = useGuestStore()
const selected = ref<string[]>([])
const saving = ref(false)

const groups = computed(() => {
  const map = new Map<string, HotelService[]>()
  for (const item of guests.catalog) {
    const list = map.get(item.group) ?? []
    list.push(item)
    map.set(item.group, list)
  }
  return [...map.entries()]
})

onMounted(async () => {
  await guests.loadCatalog()
  selected.value = [...(guests.current?.serviceIds ?? [])]
})

async function submit() {
  if (!auth.user) return
  saving.value = true
  try {
    await guests.saveServices(auth.user.email, selected.value)
    ElMessage.success('酒店服务需求已提交')
  } finally {
    saving.value = false
  }
}
</script>

<template>
  <main class="services">
    <section class="hud-panel">
      <div class="panel-title">
        <span>酒店服务</span>
        <em>已选 {{ selected.length }} 项</em>
      </div>
      <div class="pad">
        <p class="page-lead">勾选本次入住需要的配套服务，确认后提交到酒店管理端。</p>
        <div v-for="[group, items] in groups" :key="group" class="group">
          <h3>{{ group }}</h3>
          <div class="items">
            <label v-for="item in items" :key="item.id" class="item" :class="{ on: selected.includes(item.id) }">
              <input v-model="selected" type="checkbox" :value="item.id" />
              <span>
                <strong>{{ item.name }}</strong>
                <small>{{ item.description }}</small>
              </span>
            </label>
          </div>
        </div>
        <button class="gold-btn" type="button" :disabled="saving" @click="submit">确认并提交服务</button>
      </div>
    </section>
  </main>
</template>

<style scoped>
.services {
  height: 100%;
  overflow: auto;
  padding: 20px;
}

.pad {
  padding: 22px 24px 28px;
}

.group {
  margin: 8px 0 22px;
}

h3 {
  margin: 0 0 12px;
  font-size: 14px;
  letter-spacing: 0.08em;
  color: var(--cyan);
}

.items {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(260px, 1fr));
  gap: 10px;
}

.item {
  display: flex;
  align-items: flex-start;
  gap: 12px;
  padding: 14px 14px;
  border: 1px solid var(--line);
  border-radius: var(--radius-sm);
  background: rgba(7, 12, 20, 0.42);
  cursor: pointer;
}

.item:hover {
  border-color: var(--line-strong);
}

.item.on {
  border-color: var(--cyan);
  background: var(--cyan-dim);
  box-shadow: 0 0 18px rgba(90, 210, 255, 0.1);
}

.item input {
  margin-top: 3px;
  accent-color: var(--cyan);
}

.item strong {
  display: block;
}

.item small {
  display: block;
  margin-top: 4px;
  color: var(--muted);
}

.gold-btn {
  margin-top: 8px;
}

.panel-title em {
  color: var(--muted);
  font-style: normal;
}
</style>
