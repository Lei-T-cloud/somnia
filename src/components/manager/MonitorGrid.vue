<script setup lang="ts">
import { computed } from 'vue'
import type { RoomState } from '@/types'

const props = defineProps<{
  rooms: RoomState[]
}>()

const feeds = computed(() => {
  const floors = [1, 2, 3].map((floor) => {
    const list = props.rooms.filter((room) => room.floor === floor)
    const occ = list.filter((room) => room.occupied).length
    const avg = list.reduce((sum, room) => sum + room.env.temp, 0) / Math.max(list.length, 1)
    return {
      id: `${floor}F`,
      title: `${floor}F 楼层感知`,
      meta: `在住 ${occ}/${list.length}`,
      value: `${avg.toFixed(1)}°C`,
      live: floor === 2,
    }
  })
  const avgAll = props.rooms.reduce((sum, room) => sum + room.env.temp, 0) / Math.max(props.rooms.length, 1)
  floors.push({
    id: 'LOBBY',
    title: '大堂总览',
    meta: `12 间客房`,
    value: `${avgAll.toFixed(1)}°C`,
    live: false,
  })
  return floors
})
</script>

<template>
  <section class="feeds">
    <article v-for="feed in feeds" :key="feed.id" :class="{ live: feed.live }">
      <header>
        <span>{{ feed.title }}</span>
        <em>{{ feed.live ? '仿真中' : '待机' }}</em>
      </header>
      <div class="screen">
        <i />
        <strong>{{ feed.value }}</strong>
        <small>{{ feed.meta }}</small>
      </div>
    </article>
  </section>
</template>

<style scoped>
.feeds {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 8px;
  padding: 10px;
}

article {
  border: 1px solid var(--line);
  border-radius: 4px;
  overflow: hidden;
  background: #070c14;
}

article.live {
  border-color: var(--line-strong);
}

header {
  display: flex;
  justify-content: space-between;
  padding: 6px 8px;
  font-size: 11px;
  letter-spacing: 0.08em;
  color: var(--muted);
  border-bottom: 1px solid var(--line);
}

header em {
  font-style: normal;
  color: var(--cyan);
}

.screen {
  position: relative;
  height: 88px;
  display: grid;
  place-content: center;
  text-align: center;
  background:
    radial-gradient(circle at 30% 20%, rgba(62, 199, 255, 0.16), transparent 40%),
    repeating-linear-gradient(to bottom, transparent, transparent 3px, rgba(62, 199, 255, 0.05) 4px);
}

.screen i {
  position: absolute;
  inset: 0;
  background: linear-gradient(180deg, transparent, rgba(62, 199, 255, 0.08), transparent);
  animation: scan 3.6s linear infinite;
}

strong {
  position: relative;
  font-family: var(--mono);
  font-size: 20px;
}

small {
  position: relative;
  color: var(--muted);
}

@keyframes scan {
  from { transform: translateY(-100%); }
  to { transform: translateY(100%); }
}
</style>
