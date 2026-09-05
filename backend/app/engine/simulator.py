AMBIENT_TEMP = 26.2
AMBIENT_HUMIDITY = 47

LIGHT_LUX = {"off": 4, "nightlight": 18, "dim": 42, "soft": 78}
CURTAIN_DAYLIGHT = {"closed": 0, "half": 22, "open": 48}
WHITE_NOISE_DB = {"off": 0, "rain": 12, "ocean": 11, "fan": 9, "music": 10}


def _approach(current: float, target: float, rate: float) -> float:
    return current + (target - current) * rate


def derive_light(devices: dict) -> float:
    return LIGHT_LUX.get(devices.get("lighting"), 4) + CURTAIN_DAYLIGHT.get(devices.get("curtain"), 0)


def derive_noise(devices: dict) -> float:
    return 26 + WHITE_NOISE_DB.get(devices.get("whiteNoise"), 0) + (3 if devices.get("acOn") else 0)


def tick_environment(env: dict, devices: dict) -> dict:
    temp_target = devices["targetTemp"] if devices.get("acOn") else AMBIENT_TEMP
    humidity_target = devices["targetHumidity"] if devices.get("humidifierOn") else AMBIENT_HUMIDITY
    temp_rate = 0.14 if devices.get("acOn") else 0.035
    humidity_rate = 0.12 if devices.get("humidifierOn") else 0.04
    return {
        "temp": round(_approach(env["temp"], temp_target, temp_rate), 1),
        "humidity": round(_approach(env["humidity"], humidity_target, humidity_rate), 1),
        "light": derive_light(devices),
        "noise": derive_noise(devices),
    }


def tick_room(room: dict) -> dict:
    env = tick_environment(room["env"], room["devices"])
    history = (room.get("history") or []) + [env["temp"]]
    next_room = dict(room)
    next_room["env"] = env
    next_room["history"] = history[-24:]
    return next_room
