from django.utils import timezone

from .models import Guest, GuestStay, Room


def check_in(email: str, nickname: str, room_id: str) -> GuestStay:
    stay, _ = GuestStay.objects.update_or_create(
        guest_email=email,
        defaults={
            "nickname": nickname,
            "room_id": room_id,
            "status": "checked_in",
            "selected_at": timezone.now(),
            "checked_out_at": None,
        },
    )
    return stay


def check_out(email: str) -> GuestStay | None:
    stay = GuestStay.objects.filter(guest_email=email).first()
    if not stay:
        return None
    stay.status = "checked_out"
    stay.checked_out_at = timezone.now()
    stay.save(update_fields=["status", "checked_out_at"])
    return stay


def release_guest_rooms(email: str) -> None:
    Room.objects.filter(guest_email=email).update(occupied=False, guest_email=None, scene_applied=False)
    Guest.objects.filter(email=email).update(selected_room_id=None)


def checkout_guest(email: str) -> None:
    release_guest_rooms(email)
    check_out(email)
