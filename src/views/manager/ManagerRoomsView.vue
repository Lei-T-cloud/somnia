<script setup lang="ts">
import { onMounted, ref } from 'vue'
import { ElMessage } from 'element-plus'
import { apiError } from '@/api/client'
import { useHotelStore } from '@/stores/hotel'

const hotel = useHotelStore()
const uploading = ref<string | null>(null)

onMounted(async () => {
  await hotel.hydrate()
})

async function onFile(roomId: string, event: Event) {
  const input = event.target as HTMLInputElement
  const file = input.files?.[0]
  input.value = ''
  if (!file) return
  uploading.value = roomId
  try {
    await hotel.uploadPhoto(roomId, file)
    ElMessage.success(`${roomId} 实景图已更新`)
  } catch (error) {
    ElMessage.error(apiError(error, '实景图上传失败'))
  } finally {
    uploading.value = null
  }
}
</script>

<template>
  <main class="rooms">
    <section class="hud-panel intro">
      <div class="panel-title"><span>房间更新</span><em>实景图</em></div>
      <p>为每间客房上传或更换实景图。住客在「房间选择」中点选房间后，会在右上角看到这里维护的画面。</p>
    </section>
    <div class="grid">
      <article v-for="room in hotel.rooms" :key="room.id" class="hud-panel card">
        <div class="panel-title">
          <span>{{ room.name }}</span>
          <em>{{ room.floor }}F</em>
        </div>
        <div class="frame">
          <img v-if="room.photoUrl" :src="room.photoUrl" :alt="room.name" />
          <p v-else>尚未上传实景图</p>
        </div>
        <label class="upload">
          <input type="file" accept="image/*" @change="onFile(room.id, $event)" />
          {{ uploading === room.id ? '上传中…' : '更新实景图' }}
        </label>
      </article>
    </div>
  </main>
</template>

<style scoped>
.rooms {
  height: 100%;
  overflow: auto;
  padding: 16px;
}

.intro p {
  margin: 0;
  padding: 16px 18px 18px;
  color: var(--muted);
}

.grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(250px, 1fr));
  gap: 14px;
  margin-top: 14px;
}

.card {
  overflow: hidden;
}

.frame {
  height: 156px;
  background: #070b12;
  display: grid;
  place-items: center;
  overflow: hidden;
  margin: 10px 10px 0;
  border-radius: 8px;
}

.frame img {
  width: 100%;
  height: 100%;
  object-fit: cover;
}

.frame p {
  color: var(--muted);
  font-size: 13px;
}

.upload {
  display: block;
  margin: 10px;
  padding: 9px 12px;
  text-align: center;
  cursor: pointer;
  background: linear-gradient(180deg, #7adfef, var(--cyan));
  color: #041018;
  font-weight: 700;
  border-radius: var(--radius-sm);
}

.upload:hover {
  filter: brightness(1.05);
}

.upload input {
  display: none;
}

.panel-title em {
  color: var(--muted);
  font-style: normal;
}
</style>
