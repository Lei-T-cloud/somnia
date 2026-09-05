import json

from sqlalchemy.orm import Session

from .engine.simulator import derive_light, derive_noise, tick_room
from .models import Guest, HotelMeta, Room
from .serialize import room_to_dict


def get_meta(db: Session) -> HotelMeta:
    meta = db.get(HotelMeta, 1)
    if not meta:
        meta = HotelMeta(id=1, simulating=True, trend_json="[]")
        db.add(meta)
        db.commit()
        db.refresh(meta)
    return meta


def snapshot_trend(rooms: list[dict]) -> dict:
    count = max(len(rooms), 1)
    avg_temp = round(sum(room["env"]["temp"] for room in rooms) / count, 1)
    avg_humidity = round(sum(room["env"]["humidity"] for room in rooms) / count, 1)
    return {"temp": avg_temp, "humidity": avg_humidity}


def build_overview(db: Session) -> dict:
    rooms = [room_to_dict(item) for item in db.query(Room).all()]
    guests = {item.email: item for item in db.query(Guest).all()}
    occupied = [room for room in rooms if room["occupied"]]
    pending = 0
    for room in occupied:
        guest = guests.get(room["guestEmail"] or "")
        has_portrait = bool(guest and guest.portrait_json)
        if has_portrait and not room["sceneApplied"]:
            pending += 1
    snap = snapshot_trend(rooms)
    return {
        "occupiedCount": len(occupied),
        "vacantCount": len(rooms) - len(occupied),
        "avgTemp": snap["temp"],
        "avgHumidity": snap["humidity"],
        "pendingAdaptCount": pending,
    }


def persist_room_dict(db: Session, room: Room, data: dict) -> None:
    room.occupied = data["occupied"]
    room.guest_email = data["guestEmail"]
    room.scene_applied = data["sceneApplied"]
    room.env_json = json.dumps(data["env"])
    room.devices_json = json.dumps(data["devices"])
    room.history_json = json.dumps(data["history"])


def tick_hotel(db: Session) -> None:
    meta = get_meta(db)
    if not meta.simulating:
        return
    rooms = list(db.query(Room).all())
    next_rooms = []
    for row in rooms:
        data = tick_room(room_to_dict(row))
        persist_room_dict(db, row, data)
        next_rooms.append(data)
    trend = json.loads(meta.trend_json or "[]")
    trend.append(snapshot_trend(next_rooms))
    meta.trend_json = json.dumps(trend[-36:])
    db.commit()


def apply_device_patch(room: Room, patch: dict) -> dict:
    data = room_to_dict(room)
    devices = {**data["devices"], **{key: value for key, value in patch.items() if value is not None}}
    data["devices"] = devices
    data["sceneApplied"] = False
    data["env"] = {
        **data["env"],
        "light": derive_light(devices),
        "noise": derive_noise(devices),
    }
    return data
