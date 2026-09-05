<script setup lang="ts">
import { computed, nextTick, onBeforeUnmount, ref, watch } from 'vue'
import type { CorridorCamera } from '@/types'

const props = defineProps<{
  camera: CorridorCamera
  stream: MediaStream | null
  streamUrl: string
  active?: boolean
  size?: 'focus' | 'tile'
  temp?: number
  humidity?: number
}>()

const emit = defineEmits<{
  select: []
}>()

const videoRef = ref<HTMLVideoElement | null>(null)

const urlKind = computed(() => {
  const url = props.streamUrl
  if (!url) return 'none'
  if (/\.(mjpg|mjpeg|cgi)(\?|$)/i.test(url) || /mjpg|mjpeg|snapshot/i.test(url)) return 'mjpeg'
  return 'video'
})

const live = computed(() => Boolean(props.stream) || Boolean(props.streamUrl))

async function bindVideo(stream: MediaStream | null) {
  await nextTick()
  const el = videoRef.value
  if (!el) return
  if (el.srcObject !== stream) el.srcObject = stream
  if (stream) {
    el.muted = true
    void el.play().catch(() => undefined)
  }
}

watch(
  () => props.stream,
  (stream) => {
    void bindVideo(stream)
  },
  { immediate: true },
)

onBeforeUnmount(() => {
  if (videoRef.value) videoRef.value.srcObject = null
})
</script>

<template>
  <article class="feed" :class="[size || 'tile', { on: active, live }]" @click="emit('select')">
    <header>
      <b>CAM-{{ camera.floor }}F</b>
      <em>{{ live ? 'LIVE' : 'OFF' }}</em>
    </header>
    <div class="stage">
      <video ref="videoRef" autoplay muted playsinline :class="{ hidden: !stream }" />
      <img v-if="!stream && urlKind === 'mjpeg'" :src="streamUrl" alt="走廊摄像头" />
      <video
        v-else-if="!stream && urlKind === 'video' && streamUrl"
        :src="streamUrl"
        autoplay
        muted
        playsinline
      />
      <div v-if="!live" class="empty">
        <strong>{{ camera.floor }}F 走廊</strong>
        <span>等待接入本机或网络摄像头</span>
      </div>
      <i>仅楼道 · 禁止客房内</i>
    </div>
    <footer v-if="temp != null">
      <span>{{ camera.name }}</span>
      <span>{{ temp.toFixed(1) }}°C / {{ humidity?.toFixed(0) }}%</span>
    </footer>
  </article>
</template>

<style scoped>
.feed {
  display: grid;
  grid-template-rows: auto minmax(0, 1fr) auto;
  min-width: 0;
  min-height: 0;
  border: 1px solid var(--line);
  background: #070b12;
  cursor: pointer;
  border-radius: 12px;
  overflow: hidden;
}

.feed.on {
  border-color: var(--cyan);
  box-shadow: 0 0 20px rgba(90, 210, 255, 0.16);
}

header,
footer {
  display: flex;
  justify-content: space-between;
  gap: 8px;
  padding: 6px 10px;
  font-size: 12px;
  letter-spacing: 0.1em;
  font-family: var(--mono);
  color: var(--cyan);
}

footer {
  color: var(--muted);
  border-top: 1px solid var(--line);
}

header em {
  color: var(--alert);
  font-style: normal;
}

.live header em {
  color: var(--green);
}

.stage {
  position: relative;
  min-height: 0;
  background: #041018;
}

video,
img {
  display: block;
  width: 100%;
  height: 100%;
  object-fit: cover;
  background: #000;
}

.tile .stage {
  height: 132px;
}

.focus .stage {
  height: 100%;
  min-height: 280px;
}

video.hidden {
  display: none;
}

.empty {
  height: 100%;
  display: grid;
  place-content: center;
  gap: 6px;
  text-align: center;
  color: var(--muted);
}

.empty strong {
  color: var(--text);
}

i {
  position: absolute;
  right: 8px;
  bottom: 8px;
  font-style: normal;
  padding: 2px 6px;
  font-size: 11px;
  color: var(--muted);
  background: rgba(7, 11, 20, 0.72);
}
</style>
