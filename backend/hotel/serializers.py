import json

from .models import Guest, Room


def guest_to_dict(guest: Guest) -> dict:
    service_ids = [choice.service_id for choice in guest.service_choices.all()] if guest.pk else []
    return {
        "email": guest.email,
        "nickname": guest.nickname,
        "preference": json.loads(guest.preference_json) if guest.preference_json else None,
        "portrait": json.loads(guest.portrait_json) if guest.portrait_json else None,
        "selectedRoomId": guest.selected_room_id,
        "serviceIds": service_ids,
        "updatedAt": guest.updated_at,
    }


def service_to_dict(service) -> dict:
    return {
        "id": service.id,
        "name": service.name,
        "group": service.group,
        "description": service.description,
    }


def room_to_dict(room: Room) -> dict:
    return {
        "id": room.id,
        "floor": room.floor,
        "name": room.name,
        "occupied": room.occupied,
        "guestEmail": room.guest_email,
        "sceneApplied": room.scene_applied,
        "photoUrl": room.photo.url if room.photo else None,
        "env": json.loads(room.env_json),
        "devices": json.loads(room.devices_json),
        "history": json.loads(room.history_json),
    }


def apply_room_dict(room: Room, data: dict) -> None:
    room.occupied = data["occupied"]
    room.guest_email = data["guestEmail"]
    room.scene_applied = data["sceneApplied"]
    room.env_json = json.dumps(data["env"], ensure_ascii=False)
    room.devices_json = json.dumps(data["devices"], ensure_ascii=False)
    room.history_json = json.dumps(data["history"], ensure_ascii=False)
