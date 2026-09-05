import json

from .models import Guest, Room


def guest_to_dict(guest: Guest) -> dict:
    return {
        "email": guest.email,
        "nickname": guest.nickname,
        "preference": json.loads(guest.preference_json) if guest.preference_json else None,
        "portrait": json.loads(guest.portrait_json) if guest.portrait_json else None,
        "updatedAt": guest.updated_at,
    }


def room_to_dict(room: Room) -> dict:
    return {
        "id": room.id,
        "floor": room.floor,
        "name": room.name,
        "occupied": room.occupied,
        "guestEmail": room.guest_email,
        "sceneApplied": room.scene_applied,
        "env": json.loads(room.env_json),
        "devices": json.loads(room.devices_json),
        "history": json.loads(room.history_json),
    }
