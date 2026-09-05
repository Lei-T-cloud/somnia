<script setup lang="ts">
import { computed } from 'vue'
import { TresCanvas } from '@tresjs/core'
import { OrbitControls } from '@tresjs/cientos'
import HotelRoomMesh from './HotelRoomMesh.vue'
import HotelMonitorLayer from './HotelMonitorLayer.vue'
import { CORRIDOR_CAMERAS } from '@/data/cameras'
import type { ColorMode, RoomState, TwinSceneMode, ViewPreset } from '@/types'

const props = withDefaults(
  defineProps<{
    rooms: RoomState[]
    selectedId: string | null
    colorMode: ColorMode
    portraitMap: Record<string, boolean>
    viewPreset: ViewPreset
    sceneMode?: TwinSceneMode
    selectedCameraId?: string | null
  }>(),
  {
    sceneMode: 'climate',
    selectedCameraId: null,
  },
)

const emit = defineEmits<{
  select: [id: string]
  dblclick: [id: string]
  selectCorridor: [id: string]
  selectCamera: [id: string]
}>()

const PRESETS: Record<ViewPreset, { pos: [number, number, number]; target: [number, number, number] }> = {
  front: { pos: [0, 8.8, 18.2], target: [0, 3.8, 0] },
  iso: { pos: [13.5, 11.2, 13.5], target: [0, 3.8, 0] },
  top: { pos: [0.01, 24, 0.01], target: [0, 0, 0] },
}

const camera = computed(() => PRESETS[props.viewPreset])

/** 预留 gltf 替换口：若提供地址，可替换程序化楼体。首期不依赖。 */
const HOTEL_GLTF_URL: string | null = null
void HOTEL_GLTF_URL
</script>

<template>
  <div class="scene-host">
    <TresCanvas clear-color="#070b12" :shadows="true">
      <TresPerspectiveCamera :key="viewPreset" :position="camera.pos" :fov="36" :look-at="camera.target" />
      <OrbitControls
        :key="viewPreset + '-orbit'"
        :enable-damping="true"
        :min-distance="10"
        :max-distance="30"
        :max-polar-angle="Math.PI / 2.12"
        :target="camera.target"
      />
      <TresAmbientLight :intensity="0.48" color="#d7e3f2" />
      <TresHemisphereLight :args="['#b9c8dc', '#1a1520', 0.42]" />
      <TresDirectionalLight :position="[14, 22, 10]" :intensity="1.15" :cast-shadow="true" color="#dff6ff" />
      <TresPointLight :position="[0, 10, 0]" :intensity="6" color="#3ec7ff" :distance="18" />

      <TresMesh :position="[0, -0.12, 0]" :receive-shadow="true">
        <TresCylinderGeometry :args="[16, 16, 0.16, 48]" />
        <TresMeshStandardMaterial color="#0a1018" :roughness="0.9" />
      </TresMesh>

      <TresMesh v-for="floor in [1, 2, 3]" :key="floor" :position="[0, (floor - 1) * 3.2, 0]" :receive-shadow="true">
        <TresBoxGeometry :args="[11.6, 0.16, 11.6]" />
        <TresMeshStandardMaterial color="#1b2433" :metalness="0.2" :roughness="0.55" />
      </TresMesh>

      <TresMesh :position="[0, 4.7, 0]">
        <TresBoxGeometry :args="[1.15, 9.6, 1.15]" />
        <TresMeshStandardMaterial color="#2a3344" :metalness="0.3" :roughness="0.4" />
      </TresMesh>

      <HotelRoomMesh
        v-for="room in rooms"
        :key="room.id"
        :room="room"
        :selected="room.id === selectedId"
        :color-mode="colorMode"
        :has-portrait="Boolean(room.guestEmail && portraitMap[room.guestEmail])"
        @select="emit('select', $event)"
        @dblclick="emit('dblclick', $event)"
      />

      <HotelMonitorLayer
        v-if="sceneMode === 'monitor'"
        :cameras="CORRIDOR_CAMERAS"
        :selected-id="selectedCameraId"
        @select-corridor="emit('selectCorridor', $event)"
        @select-camera="emit('selectCamera', $event)"
      />
    </TresCanvas>
  </div>
</template>

<style scoped>
.scene-host {
  width: 100%;
  height: 100%;
  min-height: 0;
}

.scene-host :deep(canvas) {
  display: block;
  width: 100% !important;
  height: 100% !important;
}
</style>
