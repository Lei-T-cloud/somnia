from copy import deepcopy

SCENE_NAMES = {
    "deep-aid": "深度助眠",
    "business-quick": "商务快眠",
    "wellness": "康养舒眠",
}

SCENE_SUMMARIES = {
    "deep-aid": "压低光线与突发噪音，以连续深睡为目标。",
    "business-quick": "压缩入睡时间，兼顾清晨清醒与节奏效率。",
    "wellness": "温和温湿与舒缓声景，服务康养与敏感受众。",
}

SCENE_DEFAULTS = {
    "deep-aid": {
        "acOn": True,
        "targetTemp": 21.5,
        "targetHumidity": 50,
        "humidifierOn": True,
        "lighting": "off",
        "curtain": "closed",
        "whiteNoise": "rain",
        "fragranceOn": False,
    },
    "business-quick": {
        "acOn": True,
        "targetTemp": 23,
        "targetHumidity": 45,
        "humidifierOn": False,
        "lighting": "nightlight",
        "curtain": "half",
        "whiteNoise": "fan",
        "fragranceOn": False,
    },
    "wellness": {
        "acOn": True,
        "targetTemp": 24,
        "targetHumidity": 55,
        "humidifierOn": True,
        "lighting": "dim",
        "curtain": "half",
        "whiteNoise": "ocean",
        "fragranceOn": True,
    },
}

STAY_LABEL = {
    "business": "商务",
    "wellness": "康养",
    "family": "亲子",
    "leisure": "休闲",
}


def calc_sleep_hours(bedtime: str, wakeup: str) -> float:
    bh, bm = [int(part) for part in bedtime.split(":")]
    wh, wm = [int(part) for part in wakeup.split(":")]
    start = bh * 60 + bm
    end = wh * 60 + wm
    if end <= start:
        end += 24 * 60
    return round((end - start) / 60, 1)


def pick_scene(pref: dict, hours: float, reasons: list[str]) -> str:
    issues = pref.get("issues") or []
    insomnia = "insomnia" in issues
    light_sleeper = "light-sleeper" in issues
    allergy = "allergy" in issues
    stay = pref.get("stayScene")

    if (insomnia or light_sleeper) and stay != "wellness":
        if insomnia:
            reasons.append("存在失眠主诉，规则优先保证连续深睡。")
        if light_sleeper:
            reasons.append("易醒倾向明显，降低光线突变与噪音峰值。")
        return "deep-aid"

    if stay == "wellness" or pref.get("ageGroup") == "51+" or allergy:
        if stay == "wellness":
            reasons.append("入住场景为康养，采用更温和的温湿与声景。")
        if pref.get("ageGroup") == "51+":
            reasons.append("年龄段偏高，避免过冷过暗的刺激性设定。")
        if allergy:
            reasons.append("存在过敏问题，提高湿度并开启加湿器。")
        if insomnia or light_sleeper:
            reasons.append("康养场景叠加睡眠困扰，仍保持舒缓节律。")
        return "wellness"

    if stay == "business" or hours <= 6.5:
        if stay == "business":
            reasons.append("商务入住，强调快速入睡与清晨清醒。")
        if hours <= 6.5:
            reasons.append(f"睡眠窗口约 {hours} 小时，压缩助眠流程。")
        return "business-quick"

    reasons.append(f"入住场景为{STAY_LABEL.get(stay, stay)}，默认以深度连续睡眠为目标。")
    return "deep-aid"


def derive_sleep_portrait(pref: dict) -> dict:
    reasons: list[str] = []
    hours = calc_sleep_hours(pref["bedtime"], pref["wakeup"])
    scene_id = pick_scene(pref, hours, reasons)
    settings = deepcopy(SCENE_DEFAULTS[scene_id])
    settings["targetTemp"] = pref["preferredTemp"]
    settings["targetHumidity"] = pref["preferredHumidity"]
    reasons.append(f"沿用住客偏好温度 {pref['preferredTemp']}°C、湿度 {pref['preferredHumidity']}%。")

    if pref["light"] == "dark":
        settings["lighting"] = "off"
        settings["curtain"] = "closed"
        reasons.append("光线偏好全黑，关闭灯光并落帘。")
    elif pref["light"] == "dim":
        settings["lighting"] = "dim"
        settings["curtain"] = "half"
        reasons.append("光线偏好微光，保留低照度与半开窗帘。")
    else:
        settings["lighting"] = "nightlight"
        settings["curtain"] = "closed"
        reasons.append("光线偏好夜灯，保留定向微光、窗帘闭合以免晨光干扰。")

    if pref["sound"] == "silent":
        settings["whiteNoise"] = "off"
        reasons.append("声音偏好绝对安静，关闭白噪音。")
    elif pref["sound"] == "white-noise":
        settings["whiteNoise"] = "ocean" if scene_id == "wellness" else "rain"
        reasons.append("声音偏好白噪音，按场景匹配雨声或海潮。")
    else:
        settings["whiteNoise"] = "music"
        reasons.append("声音偏好轻音乐，入睡阶段播放低频曲目。")

    issues = pref.get("issues") or []
    if "allergy" in issues:
        settings["humidifierOn"] = True
        settings["targetHumidity"] = max(settings["targetHumidity"], 50)
    if "insomnia" in issues:
        settings["targetTemp"] = min(settings["targetTemp"], 22.5)
        settings["lighting"] = "off"
        settings["curtain"] = "closed"
        if settings["whiteNoise"] == "off":
            settings["whiteNoise"] = "rain"
        reasons.append("失眠叠加：略降室温、全黑、必要时补雨声掩蔽。")
    if "snoring" in issues:
        settings["targetTemp"] = min(settings["targetTemp"], 23)
        reasons.append("打鼾关注：避免过高室温加重气道干燥。")
    if str(pref.get("fragrance") or "").strip():
        settings["fragranceOn"] = True
        reasons.append(f"启用睡前香氛（{pref['fragrance']}）。")

    tags = [SCENE_NAMES[scene_id], STAY_LABEL.get(pref["stayScene"], pref["stayScene"]), f"{hours}h 睡眠窗"]
    if "insomnia" in issues:
        tags.append("失眠")
    if "light-sleeper" in issues:
        tags.append("易醒")
    if "snoring" in issues:
        tags.append("打鼾")
    if "allergy" in issues:
        tags.append("过敏")
    if pref.get("pillow") == "firm":
        tags.append("硬枕")
    if pref.get("mattress") == "soft":
        tags.append("软垫")

    return {
        "sceneId": scene_id,
        "sceneName": SCENE_NAMES[scene_id],
        "sceneSummary": SCENE_SUMMARIES[scene_id],
        "reasons": reasons,
        "settings": settings,
        "tags": tags,
    }
