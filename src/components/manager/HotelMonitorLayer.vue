<script setup lang="ts">
import { Html } from '@tresjs/cientos'
import type { CorridorCamera } from '@/types'

defineProps<{
  cameras: CorridorCamera[]
  selectedId: string | null
}>()

const emit = defineEmits<{
  selectCorridor: [id: string]
  selectCamera: [id: string]
}>()
</script>

<template>
  <TresGroup v-for="cam in cameras" :key="cam.id">
    <TresMesh
      :position="[0, (cam.floor - 1) * 3.2 + 0.22, 0]"
      :rotation="[-Math.PI / 2, 0, 0]"
      @click.stop="emit('selectCorridor', cam.id)"
    >
      <TresPlaneGeometry :args="[11.4, 2.35]" />
      <TresMeshStandardMaterial
        :color="selectedId === cam.id ? '#3ec7ff' : '#8b97a8'"
        :transparent="true"
        :opacity="selectedId === cam.id ? 0.28 : 0.1"
        :metalness="0.1"
        :roughness="0.8"
      />
    </TresMesh>
    <TresMesh
      :position="[0, (cam.floor - 1) * 3.2 + 0.22, 0]"
      :rotation="[-Math.PI / 2, 0, Math.PI / 2]"
      @click.stop="emit('selectCorridor', cam.id)"
    >
      <TresPlaneGeometry :args="[11.4, 2.35]" />
      <TresMeshStandardMaterial
        :color="selectedId === cam.id ? '#3ec7ff' : '#8b97a8'"
        :transparent="true"
        :opacity="selectedId === cam.id ? 0.28 : 0.1"
        :metalness="0.1"
        :roughness="0.8"
      />
    </TresMesh>

    <TresMesh
      v-for="(arm, index) in cam.coverages"
      v-show="selectedId === cam.id"
      :key="`${cam.id}-cov-${index}`"
      :position="arm.center"
      @click.stop="emit('selectCorridor', cam.id)"
    >
      <TresBoxGeometry :args="arm.size" />
      <TresMeshStandardMaterial
        color="#3ec7ff"
        :transparent="true"
        :opacity="0.18"
        :depth-write="false"
      />
    </TresMesh>

    <TresGroup :position="cam.position">
      <TresMesh @click.stop="emit('selectCamera', cam.id)">
        <TresBoxGeometry :args="[0.38, 0.22, 0.28]" />
        <TresMeshStandardMaterial
          :color="selectedId === cam.id ? '#3ec7ff' : '#d7e3f2'"
          :emissive="selectedId === cam.id ? '#3ec7ff' : '#8b97a8'"
          :emissive-intensity="selectedId === cam.id ? 0.7 : 0.2"
        />
      </TresMesh>
      <TresMesh :position="[0, -0.18, 0]" :rotation="[Math.PI / 2, 0, 0]" @click.stop="emit('selectCamera', cam.id)">
        <TresConeGeometry :args="[0.16, 0.28, 8]" />
        <TresMeshStandardMaterial color="#3ec7ff" :transparent="true" :opacity="0.55" />
      </TresMesh>
      <Html center :distance-factor="10" :position="[0, 0.38, 0]" :occlude="false">
        <div class="cam" :class="{ on: selectedId === cam.id }">{{ cam.floor }}F 监控</div>
      </Html>
    </TresGroup>
  </TresGroup>
</template>

<style scoped>
.cam {
  font-size: 11px;
  letter-spacing: 0.08em;
  padding: 2px 6px;
  color: #d9f4ff;
  background: rgba(7, 11, 20, 0.75);
  border: 1px solid rgba(62, 199, 255, 0.35);
  pointer-events: none;
  white-space: nowrap;
  font-family: "JetBrains Mono", "Cascadia Mono", monospace;
}

.cam.on {
  color: #041018;
  background: #3ec7ff;
}
</style>
