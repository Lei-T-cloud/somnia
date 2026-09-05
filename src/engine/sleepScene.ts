import type {
  DeviceSettings,
  SceneId,
  SleepPortrait,
  SleepPreference,
} from '@/types'

export const SCENE_NAMES: Record<SceneId, string> = {
  'deep-aid': '深度助眠',
  'business-quick': '商务快眠',
  wellness: '康养舒眠',
}

export const SCENE_SUMMARIES: Record<SceneId, string> = {
  'deep-aid': '压低光线与突发噪音，以连续深睡为目标。',
  'business-quick': '压缩入睡时间，兼顾清晨清醒与节奏效率。',
  wellness: '温和温湿与舒缓声景，服务康养与敏感受众。',
}

export const SCENE_DEFAULTS: Record<SceneId, DeviceSettings> = {
  'deep-aid': {
    acOn: true,
    targetTemp: 21.5,
    targetHumidity: 50,
    humidifierOn: true,
    lighting: 'off',
    curtain: 'closed',
    whiteNoise: 'rain',
    fragranceOn: false,
  },
  'business-quick': {
    acOn: true,
    targetTemp: 23,
    targetHumidity: 45,
    humidifierOn: false,
    lighting: 'nightlight',
    curtain: 'half',
    whiteNoise: 'fan',
    fragranceOn: false,
  },
  wellness: {
    acOn: true,
    targetTemp: 24,
    targetHumidity: 55,
    humidifierOn: true,
    lighting: 'dim',
    curtain: 'half',
    whiteNoise: 'ocean',
    fragranceOn: true,
  },
}

const STAY_LABEL: Record<SleepPreference['stayScene'], string> = {
  business: '商务',
  wellness: '康养',
  family: '亲子',
  leisure: '休闲',
}

export function calcSleepHours(bedtime: string, wakeup: string): number {
  const [bh, bm] = bedtime.split(':').map(Number)
  const [wh, wm] = wakeup.split(':').map(Number)
  const start = bh * 60 + bm
  let end = wh * 60 + wm
  if (end <= start) end += 24 * 60
  return Math.round(((end - start) / 60) * 10) / 10
}

function pickScene(pref: SleepPreference, hours: number, reasons: string[]): SceneId {
  const insomnia = pref.issues.includes('insomnia')
  const lightSleeper = pref.issues.includes('light-sleeper')
  const allergy = pref.issues.includes('allergy')

  if ((insomnia || lightSleeper) && pref.stayScene !== 'wellness') {
    if (insomnia) reasons.push('存在失眠主诉，规则优先保证连续深睡。')
    if (lightSleeper) reasons.push('易醒倾向明显，降低光线突变与噪音峰值。')
    return 'deep-aid'
  }

  if (pref.stayScene === 'wellness' || pref.ageGroup === '51+' || allergy) {
    if (pref.stayScene === 'wellness') reasons.push('入住场景为康养，采用更温和的温湿与声景。')
    if (pref.ageGroup === '51+') reasons.push('年龄段偏高，避免过冷过暗的刺激性设定。')
    if (allergy) reasons.push('存在过敏问题，提高湿度并开启加湿器。')
    if (insomnia || lightSleeper) reasons.push('康养场景叠加睡眠困扰，仍保持舒缓节律。')
    return 'wellness'
  }

  if (pref.stayScene === 'business' || hours <= 6.5) {
    if (pref.stayScene === 'business') reasons.push('商务入住，强调快速入睡与清晨清醒。')
    if (hours <= 6.5) reasons.push(`睡眠窗口约 ${hours} 小时，压缩助眠流程。`)
    return 'business-quick'
  }

  reasons.push(`入住场景为${STAY_LABEL[pref.stayScene]}，默认以深度连续睡眠为目标。`)
  return 'deep-aid'
}

export function deriveSleepPortrait(pref: SleepPreference): SleepPortrait {
  const reasons: string[] = []
  const hours = calcSleepHours(pref.bedtime, pref.wakeup)
  const sceneId = pickScene(pref, hours, reasons)
  const settings: DeviceSettings = { ...SCENE_DEFAULTS[sceneId] }

  settings.targetTemp = pref.preferredTemp
  settings.targetHumidity = pref.preferredHumidity
  reasons.push(`沿用住客偏好温度 ${pref.preferredTemp}°C、湿度 ${pref.preferredHumidity}%。`)

  if (pref.light === 'dark') {
    settings.lighting = 'off'
    settings.curtain = 'closed'
    reasons.push('光线偏好全黑，关闭灯光并落帘。')
  } else if (pref.light === 'dim') {
    settings.lighting = 'dim'
    settings.curtain = 'half'
    reasons.push('光线偏好微光，保留低照度与半开窗帘。')
  } else {
    settings.lighting = 'nightlight'
    settings.curtain = 'closed'
    reasons.push('光线偏好夜灯，保留定向微光、窗帘闭合以免晨光干扰。')
  }

  if (pref.sound === 'silent') {
    settings.whiteNoise = 'off'
    reasons.push('声音偏好绝对安静，关闭白噪音。')
  } else if (pref.sound === 'white-noise') {
    settings.whiteNoise = sceneId === 'wellness' ? 'ocean' : 'rain'
    reasons.push('声音偏好白噪音，按场景匹配雨声或海潮。')
  } else {
    settings.whiteNoise = 'music'
    reasons.push('声音偏好轻音乐，入睡阶段播放低频曲目。')
  }

  if (pref.issues.includes('allergy')) {
    settings.humidifierOn = true
    settings.targetHumidity = Math.max(settings.targetHumidity, 50)
  }

  if (pref.issues.includes('insomnia')) {
    settings.targetTemp = Math.min(settings.targetTemp, 22.5)
    settings.lighting = 'off'
    settings.curtain = 'closed'
    if (settings.whiteNoise === 'off') settings.whiteNoise = 'rain'
    reasons.push('失眠叠加：略降室温、全黑、必要时补雨声掩蔽。')
  }

  if (pref.issues.includes('snoring')) {
    settings.targetTemp = Math.min(settings.targetTemp, 23)
    reasons.push('打鼾关注：避免过高室温加重气道干燥。')
  }

  if (pref.fragrance.trim()) {
    settings.fragranceOn = true
    reasons.push(`启用睡前香氛（${pref.fragrance}）。`)
  }

  const tags = [SCENE_NAMES[sceneId], STAY_LABEL[pref.stayScene], `${hours}h 睡眠窗`]
  if (pref.issues.includes('insomnia')) tags.push('失眠')
  if (pref.issues.includes('light-sleeper')) tags.push('易醒')
  if (pref.issues.includes('snoring')) tags.push('打鼾')
  if (pref.issues.includes('allergy')) tags.push('过敏')
  if (pref.pillow === 'firm') tags.push('硬枕')
  if (pref.mattress === 'soft') tags.push('软垫')

  return {
    sceneId,
    sceneName: SCENE_NAMES[sceneId],
    sceneSummary: SCENE_SUMMARIES[sceneId],
    reasons,
    settings,
    tags,
  }
}

export const EMPTY_PREFERENCE: SleepPreference = {
  nickname: '',
  gender: 'other',
  ageGroup: '26-35',
  stayScene: 'leisure',
  bedtime: '23:00',
  wakeup: '07:30',
  preferredTemp: 22,
  preferredHumidity: 50,
  light: 'dark',
  sound: 'white-noise',
  pillow: 'medium',
  mattress: 'medium',
  issues: [],
  fragrance: '',
  bedtimeHabit: '',
}
