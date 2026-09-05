import json

from sqlalchemy.orm import Session

from .engine.simulator import derive_light, derive_noise
from .engine.sleep_scene import derive_sleep_portrait
from .models import Account, Guest, HotelMeta, Room

DEMO_PASSWORD = "somnia123"


def _settings(**partial: object) -> dict:
    base = {
        "acOn": True,
        "targetTemp": 23,
        "targetHumidity": 50,
        "humidifierOn": False,
        "lighting": "dim",
        "curtain": "half",
        "whiteNoise": "off",
        "fragranceOn": False,
    }
    base.update(partial)
    return base


LIN = {
    "nickname": "林晚宁",
    "gender": "female",
    "ageGroup": "26-35",
    "stayScene": "leisure",
    "bedtime": "23:30",
    "wakeup": "08:00",
    "preferredTemp": 21.5,
    "preferredHumidity": 50,
    "light": "dark",
    "sound": "white-noise",
    "pillow": "medium",
    "mattress": "soft",
    "issues": ["insomnia", "light-sleeper"],
    "fragrance": "薰衣草",
    "bedtimeHabit": "睡前阅读二十分钟",
}
ZHOU = {
    "nickname": "周启明",
    "gender": "male",
    "ageGroup": "36-50",
    "stayScene": "business",
    "bedtime": "00:30",
    "wakeup": "06:30",
    "preferredTemp": 23,
    "preferredHumidity": 45,
    "light": "nightlight",
    "sound": "silent",
    "pillow": "firm",
    "mattress": "medium",
    "issues": [],
    "fragrance": "",
    "bedtimeHabit": "回邮件后即睡",
}
SU = {
    "nickname": "苏清和",
    "gender": "female",
    "ageGroup": "51+",
    "stayScene": "wellness",
    "bedtime": "21:30",
    "wakeup": "06:30",
    "preferredTemp": 24,
    "preferredHumidity": 55,
    "light": "dim",
    "sound": "white-noise",
    "pillow": "soft",
    "mattress": "soft",
    "issues": ["allergy"],
    "fragrance": "雪松",
    "bedtimeHabit": "温水泡脚",
}


def _room(room_id: str, floor: int, occupied: bool, guest_email: str | None, scene_applied: bool, temp: float, humidity: float, devices: dict) -> dict:
    env = {"temp": temp, "humidity": humidity, "light": derive_light(devices), "noise": derive_noise(devices)}
    return {
        "id": room_id,
        "floor": floor,
        "name": f"{room_id} 房",
        "occupied": occupied,
        "guest_email": guest_email,
        "scene_applied": scene_applied,
        "env": env,
        "devices": devices,
        "history": [temp],
    }


def seed_if_empty(db: Session) -> None:
    if db.get(Account, "guest@somnia.demo"):
        return

    db.add_all(
        [
            Account(email="guest@somnia.demo", password=DEMO_PASSWORD, role="guest", nickname="林晚宁"),
            Account(email="manager@somnia.demo", password=DEMO_PASSWORD, role="manager", nickname="值班经理"),
            Account(email="zhou@somnia.demo", password=DEMO_PASSWORD, role="guest", nickname="周启明"),
            Account(email="su@somnia.demo", password=DEMO_PASSWORD, role="guest", nickname="苏清和"),
            Account(email="chen@somnia.demo", password=DEMO_PASSWORD, role="guest", nickname="陈途"),
        ]
    )

    for email, pref in [
        ("guest@somnia.demo", LIN),
        ("zhou@somnia.demo", ZHOU),
        ("su@somnia.demo", SU),
    ]:
        db.add(
            Guest(
                email=email,
                nickname=pref["nickname"],
                preference_json=json.dumps(pref, ensure_ascii=False),
                portrait_json=json.dumps(derive_sleep_portrait(pref), ensure_ascii=False),
                updated_at="2026-09-05T10:00:00.000Z",
            )
        )
    db.add(Guest(email="chen@somnia.demo", nickname="陈途", preference_json=None, portrait_json=None, updated_at=None))

    rooms = [
        _room("101", 1, False, None, False, 25.8, 46, _settings(acOn=False, targetTemp=24)),
        _room("102", 1, False, None, False, 24.6, 48, _settings(acOn=False)),
        _room("103", 1, True, "chen@somnia.demo", False, 26.4, 44, _settings(acOn=True, targetTemp=24)),
        _room("104", 1, True, "su@somnia.demo", True, 24.2, 54, derive_sleep_portrait(SU)["settings"]),
        _room("201", 2, True, "zhou@somnia.demo", True, 23.4, 46, derive_sleep_portrait(ZHOU)["settings"]),
        _room("202", 2, False, None, False, 25.1, 47, _settings(acOn=False)),
        _room("203", 2, True, None, False, 27.1, 43, _settings(acOn=False, lighting="soft", curtain="open")),
        _room("204", 2, False, None, False, 22.8, 51, _settings(acOn=True, targetTemp=22)),
        _room("301", 3, False, None, False, 24.9, 49, _settings(acOn=False)),
        _room("302", 3, True, "guest@somnia.demo", False, 26.8, 45, _settings(acOn=True, targetTemp=25, lighting="soft")),
        _room("303", 3, False, None, False, 21.6, 52, _settings(acOn=True, targetTemp=21.5)),
        _room("304", 3, False, None, False, 25.4, 48, _settings(acOn=False)),
    ]
    for item in rooms:
        db.add(
            Room(
                id=item["id"],
                floor=item["floor"],
                name=item["name"],
                occupied=item["occupied"],
                guest_email=item["guest_email"],
                scene_applied=item["scene_applied"],
                env_json=json.dumps(item["env"]),
                devices_json=json.dumps(item["devices"]),
                history_json=json.dumps(item["history"]),
            )
        )

    temps = [item["env"]["temp"] for item in rooms]
    hums = [item["env"]["humidity"] for item in rooms]
    avg_temp = round(sum(temps) / len(temps), 1)
    avg_hum = round(sum(hums) / len(hums), 1)
    db.add(HotelMeta(id=1, simulating=True, trend_json=json.dumps([{"temp": avg_temp, "humidity": avg_hum}])))
    db.commit()
