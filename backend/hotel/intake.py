import json
from datetime import datetime, timezone as dt_timezone

from django.utils import timezone

from .models import Guest, GuestUpload, SleepPreferenceRecord

PREF_KEYS = (
    "nickname",
    "gender",
    "ageGroup",
    "stayScene",
    "bedtime",
    "wakeup",
    "preferredTemp",
    "preferredHumidity",
    "light",
    "sound",
    "pillow",
    "mattress",
    "issues",
    "fragrance",
    "bedtimeHabit",
)

ISSUE_LABEL = {
    "insomnia": "失眠",
    "light-sleeper": "易醒",
    "snoring": "打鼾",
    "allergy": "过敏",
}


def now_iso() -> str:
    return datetime.now(dt_timezone.utc).isoformat()


def extract_preference(data: dict) -> dict:
    pref: dict = {}
    for key in PREF_KEYS:
        if key not in data:
            continue
        value = data[key]
        if key == "issues":
            pref[key] = [str(item) for item in value] if isinstance(value, list) else []
        elif key in {"preferredTemp", "preferredHumidity"}:
            try:
                pref[key] = float(value) if key == "preferredTemp" else int(float(value))
            except (TypeError, ValueError):
                continue
        else:
            pref[key] = value if value is not None else ""
    return pref


def issues_text(issues: list) -> str:
    return "、".join(ISSUE_LABEL.get(str(item), str(item)) for item in issues)


def log_upload(kind: str, *, guest_email: str = "", room_id: str = "", summary: str = "", payload: dict | None = None) -> None:
    GuestUpload.objects.create(
        kind=kind,
        guest_email=guest_email,
        room_id=room_id or "",
        summary=summary[:200],
        payload_json=json.dumps(payload or {}, ensure_ascii=False),
    )


def sync_preference_record(guest: Guest, pref: dict, portrait: dict | None = None) -> SleepPreferenceRecord:
    scene_name = ""
    if portrait:
        scene_name = str(portrait.get("sceneName") or "")
    elif guest.portrait_json:
        try:
            scene_name = json.loads(guest.portrait_json).get("sceneName") or ""
        except json.JSONDecodeError:
            scene_name = ""
    issues = pref.get("issues") or []
    defaults = {
        "gender": str(pref.get("gender") or ""),
        "age_group": str(pref.get("ageGroup") or ""),
        "stay_scene": str(pref.get("stayScene") or ""),
        "bedtime": str(pref.get("bedtime") or ""),
        "wakeup": str(pref.get("wakeup") or ""),
        "preferred_temp": pref.get("preferredTemp"),
        "preferred_humidity": pref.get("preferredHumidity"),
        "light": str(pref.get("light") or ""),
        "sound": str(pref.get("sound") or ""),
        "pillow": str(pref.get("pillow") or ""),
        "mattress": str(pref.get("mattress") or ""),
        "issues": issues_text(issues) if isinstance(issues, list) else "",
        "fragrance": str(pref.get("fragrance") or ""),
        "bedtime_habit": str(pref.get("bedtimeHabit") or ""),
        "scene_name": scene_name,
        "uploaded_at": timezone.now(),
    }
    record, _ = SleepPreferenceRecord.objects.update_or_create(guest=guest, defaults=defaults)
    guest.gender = defaults["gender"]
    guest.age_group = defaults["age_group"]
    guest.stay_scene = defaults["stay_scene"]
    guest.bedtime = defaults["bedtime"]
    guest.wakeup = defaults["wakeup"]
    guest.preferred_temp = defaults["preferred_temp"]
    guest.preferred_humidity = defaults["preferred_humidity"]
    guest.light = defaults["light"]
    guest.sound = defaults["sound"]
    guest.pillow = defaults["pillow"]
    guest.mattress = defaults["mattress"]
    guest.issues = defaults["issues"]
    guest.fragrance = defaults["fragrance"]
    guest.bedtime_habit = defaults["bedtime_habit"]
    guest.scene_title = scene_name
    guest.preference_at = defaults["uploaded_at"]
    return record


def apply_preference(guest: Guest, pref: dict, portrait: dict) -> Guest:
    stamp = now_iso()
    guest.nickname = str(pref.get("nickname") or guest.nickname)
    guest.preference_json = json.dumps(pref, ensure_ascii=False)
    guest.portrait_json = json.dumps(portrait, ensure_ascii=False)
    guest.updated_at = stamp
    sync_preference_record(guest, pref, portrait)
    guest.save()
    log_upload(
        "preference",
        guest_email=guest.email,
        room_id=guest.selected_room_id or "",
        summary=f"{guest.nickname} 上传偏好 · {guest.scene_title or '已生成画像'}",
        payload={
            "stayScene": pref.get("stayScene"),
            "preferredTemp": pref.get("preferredTemp"),
            "preferredHumidity": pref.get("preferredHumidity"),
            "sceneName": guest.scene_title,
        },
    )
    return guest


def mark_room_selected(guest: Guest, room_id: str) -> Guest:
    guest.selected_room_id = room_id
    guest.room_selected_at = timezone.now()
    guest.updated_at = now_iso()
    guest.save(update_fields=["selected_room_id", "room_selected_at", "updated_at"])
    log_upload(
        "select_room",
        guest_email=guest.email,
        room_id=room_id,
        summary=f"{guest.nickname} 确认选择 {room_id} 房",
        payload={"roomId": room_id},
    )
    return guest


def mark_services_submitted(guest: Guest, service_ids: list[str]) -> Guest:
    guest.services_completed = False
    guest.services_at = timezone.now()
    guest.updated_at = now_iso()
    guest.save(update_fields=["services_completed", "services_at", "updated_at"])
    log_upload(
        "services",
        guest_email=guest.email,
        room_id=guest.selected_room_id or "",
        summary=f"{guest.nickname} 提交 {len(service_ids)} 项酒店服务",
        payload={"serviceIds": service_ids},
    )
    return guest
