import json

from app.engine.simulator import derive_light, derive_noise, tick_room

from .models import Guest, HotelMeta, Room
from .serializers import apply_room_dict, room_to_dict
from .stays import check_in


def get_meta() -> HotelMeta:
    meta, _ = HotelMeta.objects.get_or_create(id=1, defaults={"simulating": True, "trend_json": "[]"})
    return meta


def snapshot_trend(rooms: list[dict]) -> dict:
    count = max(len(rooms), 1)
    return {
        "temp": round(sum(room["env"]["temp"] for room in rooms) / count, 1),
        "humidity": round(sum(room["env"]["humidity"] for room in rooms) / count, 1),
    }


def build_overview() -> dict:
    rooms = [room_to_dict(item) for item in Room.objects.all()]
    guests = {item.email: item for item in Guest.objects.all()}
    occupied = [room for room in rooms if room["occupied"]]
    pending = 0
    for room in occupied:
        guest = guests.get(room["guestEmail"] or "")
        if guest and guest.portrait_json and not room["sceneApplied"]:
            pending += 1
    snap = snapshot_trend(rooms)
    return {
        "occupiedCount": len(occupied),
        "vacantCount": len(rooms) - len(occupied),
        "avgTemp": snap["temp"],
        "avgHumidity": snap["humidity"],
        "pendingAdaptCount": pending,
    }


def bind_guest_to_room(email: str, room_id: str) -> Room | None:
    room = Room.objects.filter(id=room_id).first()
    if not room:
        return None
    if room.guest_email and room.guest_email != email:
        return None
    Room.objects.filter(guest_email=email).exclude(id=room_id).update(
        occupied=False, guest_email=None, scene_applied=False
    )
    room.occupied = True
    room.guest_email = email
    room.save(update_fields=["occupied", "guest_email"])
    guest = Guest.objects.filter(email=email).first()
    if guest:
        check_in(email, guest.nickname, room_id)
    return room


def apply_device_patch(room: Room, patch: dict) -> dict:
    data = room_to_dict(room)
    devices = {**data["devices"], **{key: value for key, value in patch.items() if value is not None}}
    data["devices"] = devices
    data["sceneApplied"] = False
    data["env"] = {**data["env"], "light": derive_light(devices), "noise": derive_noise(devices)}
    return data


def tick_hotel() -> None:
    meta = get_meta()
    if not meta.simulating:
        return
    next_rooms = []
    for row in Room.objects.all():
        data = tick_room(room_to_dict(row))
        apply_room_dict(row, data)
        row.save()
        next_rooms.append(data)
    if not next_rooms:
        return
    trend = json.loads(meta.trend_json or "[]")
    trend.append(snapshot_trend(next_rooms))
    meta.trend_json = json.dumps(trend[-36:], ensure_ascii=False)
    meta.save(update_fields=["trend_json"])
