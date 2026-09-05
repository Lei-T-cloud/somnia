<script setup lang="ts">
import { reactive, ref, watch } from 'vue'
import type { FormInstance, FormRules } from 'element-plus'
import { EMPTY_PREFERENCE } from '@/engine/sleepScene'
import type { SleepPreference } from '@/types'

const props = defineProps<{
  model: SleepPreference | null
  nicknameFallback: string
}>()

const formRef = ref<FormInstance>()
const form = reactive<SleepPreference>({
  ...EMPTY_PREFERENCE,
  nickname: props.nicknameFallback,
})

watch(
  () => props.model,
  (value) => {
    Object.assign(form, value ?? { ...EMPTY_PREFERENCE, nickname: props.nicknameFallback })
  },
  { immediate: true },
)

const rules: FormRules<SleepPreference> = {
  nickname: [{ required: true, message: '请填写昵称', trigger: 'blur' }],
  bedtime: [{ required: true, message: '请选择就寝时间', trigger: 'change' }],
  wakeup: [{ required: true, message: '请选择起床时间', trigger: 'change' }],
}

defineExpose({ form, validate: () => formRef.value?.validate() })
</script>

<template>
  <el-form ref="formRef" :model="form" :rules="rules" label-position="top" class="pref-form">
    <div class="block">
      <h3>个人信息</h3>
      <div class="row">
        <el-form-item label="昵称" prop="nickname">
          <el-input v-model="form.nickname" />
        </el-form-item>
        <el-form-item label="性别">
          <el-select v-model="form.gender">
            <el-option label="女" value="female" />
            <el-option label="男" value="male" />
            <el-option label="不愿透露" value="other" />
          </el-select>
        </el-form-item>
        <el-form-item label="年龄段">
          <el-select v-model="form.ageGroup">
            <el-option label="18–25" value="18-25" />
            <el-option label="26–35" value="26-35" />
            <el-option label="36–50" value="36-50" />
            <el-option label="51 及以上" value="51+" />
          </el-select>
        </el-form-item>
        <el-form-item label="入住场景">
          <el-select v-model="form.stayScene">
            <el-option label="商务" value="business" />
            <el-option label="康养" value="wellness" />
            <el-option label="亲子" value="family" />
            <el-option label="休闲" value="leisure" />
          </el-select>
        </el-form-item>
      </div>
    </div>

    <div class="block">
      <h3>睡眠偏好</h3>
      <div class="row">
        <el-form-item label="就寝时间" prop="bedtime">
          <el-time-picker v-model="form.bedtime" format="HH:mm" value-format="HH:mm" />
        </el-form-item>
        <el-form-item label="起床时间" prop="wakeup">
          <el-time-picker v-model="form.wakeup" format="HH:mm" value-format="HH:mm" />
        </el-form-item>
        <el-form-item :label="`偏好温度 ${form.preferredTemp}°C`">
          <el-slider v-model="form.preferredTemp" :min="18" :max="28" :step="0.5" />
        </el-form-item>
        <el-form-item :label="`偏好湿度 ${form.preferredHumidity}%`">
          <el-slider v-model="form.preferredHumidity" :min="35" :max="70" :step="1" />
        </el-form-item>
        <el-form-item label="光线">
          <el-radio-group v-model="form.light">
            <el-radio-button label="dark">全黑</el-radio-button>
            <el-radio-button label="dim">微光</el-radio-button>
            <el-radio-button label="nightlight">夜灯</el-radio-button>
          </el-radio-group>
        </el-form-item>
        <el-form-item label="声音">
          <el-radio-group v-model="form.sound">
            <el-radio-button label="silent">绝对安静</el-radio-button>
            <el-radio-button label="white-noise">白噪音</el-radio-button>
            <el-radio-button label="soft-music">轻音乐</el-radio-button>
          </el-radio-group>
        </el-form-item>
        <el-form-item label="枕头硬度">
          <el-select v-model="form.pillow">
            <el-option label="软" value="soft" />
            <el-option label="适中" value="medium" />
            <el-option label="硬" value="firm" />
          </el-select>
        </el-form-item>
        <el-form-item label="床垫软硬">
          <el-select v-model="form.mattress">
            <el-option label="软" value="soft" />
            <el-option label="适中" value="medium" />
            <el-option label="硬" value="firm" />
          </el-select>
        </el-form-item>
        <el-form-item label="睡眠问题" class="wide">
          <el-checkbox-group v-model="form.issues">
            <el-checkbox label="insomnia">失眠</el-checkbox>
            <el-checkbox label="light-sleeper">易醒</el-checkbox>
            <el-checkbox label="snoring">打鼾</el-checkbox>
            <el-checkbox label="allergy">过敏</el-checkbox>
          </el-checkbox-group>
        </el-form-item>
        <el-form-item label="香氛（可选）">
          <el-input v-model="form.fragrance" placeholder="如薰衣草、雪松" />
        </el-form-item>
        <el-form-item label="睡前习惯（可选）" class="wide">
          <el-input v-model="form.bedtimeHabit" placeholder="如阅读、泡脚、关闭通知" />
        </el-form-item>
      </div>
    </div>
  </el-form>
</template>

<style scoped>
.pref-form {
  display: grid;
  gap: 16px;
}

.block {
  padding: 16px 16px 8px;
  border: 1px solid var(--line);
  border-radius: var(--radius);
  background: rgba(7, 12, 20, 0.42);
}

h3 {
  margin: 0 0 14px;
  font-size: 15px;
  letter-spacing: 0.06em;
}

.row {
  display: grid;
  grid-template-columns: repeat(2, minmax(0, 1fr));
  gap: 4px 18px;
}

.wide {
  grid-column: 1 / -1;
}

@media (max-width: 800px) {
  .row {
    grid-template-columns: 1fr;
  }
}
</style>
