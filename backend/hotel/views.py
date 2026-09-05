import json
import secrets
from datetime import datetime, timezone

from django.http import JsonResponse
from rest_framework.decorators import api_view, parser_classes
from rest_framework.parsers import FormParser, MultiPartParser
from rest_framework.request import Request

from app.engine.simulator import derive_light, derive_noise
from app.engine.sleep_scene import derive_sleep_portrait

from .authz import current_account, require_manager, require_owner
from .intake import apply_preference, extract_preference, log_upload, mark_room_selected, mark_services_submitted, now_iso
from .models import Account, Guest, GuestServiceChoice, HotelService, Room, SessionToken
from .security import (
    hash_password,
    is_hashed,
    session_payload,
    sync_backend_user,
    valid_email,
    verify_password,
)
from .serializers import apply_room_dict, guest_to_dict, room_to_dict, service_to_dict
from .services import apply_device_patch, bind_guest_to_room, build_overview, get_meta
from .stays import checkout_guest


def fail(detail: str, status: int = 400) -> JsonResponse:
    return JsonResponse({"detail": detail}, status=status)


@api_view(["POST"])
def login(request: Request) -> JsonResponse:
    email = str(request.data.get("email") or "").strip().lower()
    password = str(request.data.get("password") or "")
    account = Account.objects.filter(email=email).first()
    if not account or not verify_password(password, account.password):
        return fail("邮箱或密码不正确")
    if account.role == "manager" and account.status != "active":
        return fail("账号待管理员审核" if account.status == "pending" else "账号未通过审核")
    if not is_hashed(account.password):
        account.password = hash_password(password)
        account.save(update_fields=["password"])
    token = secrets.token_hex(24)
    SessionToken.objects.create(token=token, email=account.email)
    return JsonResponse(session_payload(account, token))


@api_view(["POST"])
def register(request: Request) -> JsonResponse:
    email = str(request.data.get("email") or "").strip().lower()
    password = str(request.data.get("password") or "")
    nickname = str(request.data.get("nickname") or "").strip()
    role = str(request.data.get("role") or "guest").strip()
    if role not in ("guest", "manager"):
        return fail("请选择账号类型")
    if not valid_email(email):
        return fail("请输入有效邮箱")
    if len(password) < 8:
        return fail("密码至少 8 位")
    if not nickname:
        return fail("请填写姓名")
    if Account.objects.filter(email=email).exists():
        return fail("该邮箱已注册")
    pending = role == "manager"
    account = Account.objects.create(
        email=email,
        password=hash_password(password),
        role=role,
        nickname=nickname,
        status="pending" if pending else "active",
        is_owner=False,
    )
    if role == "guest":
        Guest.objects.get_or_create(email=email, defaults={"nickname": nickname})
        token = secrets.token_hex(24)
        SessionToken.objects.create(token=token, email=email)
        return JsonResponse(session_payload(account, token))
    sync_backend_user(account)
    return JsonResponse(
        {
            "pending": True,
            "email": email,
            "role": "manager",
            "nickname": nickname,
            "detail": "已提交注册，等待主管理员同意后才能登录管理端",
        }
    )


@api_view(["GET"])
def me(request: Request) -> JsonResponse:
    account = current_account(request)
    return JsonResponse(
        {
            "email": account.email,
            "role": account.role,
            "nickname": account.nickname,
            "isOwner": account.is_owner,
            "status": account.status,
        }
    )


def staff_to_dict(account: Account) -> dict:
    return {
        "email": account.email,
        "nickname": account.nickname,
        "status": account.status,
        "isOwner": account.is_owner,
    }


@api_view(["GET"])
def list_staff(request: Request) -> JsonResponse:
    require_owner(request)
    rows = [staff_to_dict(item) for item in Account.objects.filter(role="manager").order_by("-is_owner", "status", "email")]
    return JsonResponse(rows, safe=False)


@api_view(["POST"])
def review_staff(request: Request, email: str) -> JsonResponse:
    require_owner(request)
    email = email.strip().lower()
    account = Account.objects.filter(email=email, role="manager").first()
    if not account:
        return fail("员工账号不存在", 404)
    if account.is_owner:
        return fail("不能审核主管理员")
    approved = bool(request.data.get("approved"))
    account.status = "active" if approved else "rejected"
    account.save(update_fields=["status"])
    if not approved:
        SessionToken.objects.filter(email=email).delete()
    sync_backend_user(account)
    return JsonResponse(staff_to_dict(account))


@api_view(["POST"])
def logout(request: Request) -> JsonResponse:
    current_account(request)
    header = request.headers.get("Authorization") or ""
    token = header.removeprefix("Bearer ").strip()
    SessionToken.objects.filter(token=token).delete()
    return JsonResponse({"ok": True})


@api_view(["GET"])
def list_guests(request: Request) -> JsonResponse:
    current_account(request)
    guests = Guest.objects.prefetch_related("service_choices")
    return JsonResponse([guest_to_dict(item) for item in guests], safe=False)


@api_view(["POST"])
def ensure_guest(request: Request) -> JsonResponse:
    account = current_account(request)
    email = str(request.data.get("email") or "").strip().lower()
    nickname = str(request.data.get("nickname") or "").strip()
    if account.role == "guest" and account.email != email:
        return fail("只能维护本人画像", 403)
    guest, _ = Guest.objects.get_or_create(email=email, defaults={"nickname": nickname})
    return JsonResponse(guest_to_dict(guest))


@api_view(["PUT"])
def save_preference(request: Request, email: str) -> JsonResponse:
    account = current_account(request)
    email = email.strip().lower()
    if account.role == "guest" and account.email != email:
        return fail("只能维护本人画像", 403)
    pref = extract_preference(dict(request.data))
    required = ("nickname", "bedtime", "wakeup", "preferredTemp", "preferredHumidity", "light", "sound", "stayScene")
    if any(key not in pref or pref[key] in ("", None) for key in required):
        return fail("请完整填写睡眠偏好")
    portrait = derive_sleep_portrait(pref)
    guest, _ = Guest.objects.get_or_create(email=email, defaults={"nickname": pref.get("nickname") or email})
    apply_preference(guest, pref, portrait)
    room_id = guest.selected_room_id
    if not room_id:
        occupied = Room.objects.filter(guest_email=email).first()
        if occupied:
            room_id = occupied.id
            guest.selected_room_id = room_id
            guest.save(update_fields=["selected_room_id"])
    if room_id:
        bind_guest_to_room(email, room_id)
    guest = Guest.objects.prefetch_related("service_choices").get(email=guest.email)
    return JsonResponse(guest_to_dict(guest))


@api_view(["POST"])
def select_room(request: Request, email: str) -> JsonResponse:
    account = current_account(request)
    email = email.strip().lower()
    if account.role == "guest" and account.email != email:
        return fail("只能选择本人房间", 403)
    room_id = str(request.data.get("roomId") or "").strip()
    room = Room.objects.filter(id=room_id).first()
    if not room:
        return fail("房间不存在", 404)
    if room.guest_email and room.guest_email != email:
        return fail("该房间已被其他住客占用")
    guest = Guest.objects.filter(email=email).first()
    if not guest:
        return fail("住客不存在", 404)
    bound = bind_guest_to_room(email, room_id)
    if not bound:
        return fail("该房间已被其他住客占用")
    room.scene_applied = False
    room.save(update_fields=["scene_applied"])
    mark_room_selected(guest, room_id)
    guest = Guest.objects.prefetch_related("service_choices").get(email=email)
    return JsonResponse(guest_to_dict(guest))


@api_view(["GET"])
def list_services(request: Request) -> JsonResponse:
    current_account(request)
    items = [service_to_dict(item) for item in HotelService.objects.order_by("sort", "id")]
    return JsonResponse(items, safe=False)


@api_view(["PUT"])
def save_services(request: Request, email: str) -> JsonResponse:
    account = current_account(request)
    email = email.strip().lower()
    if account.role == "guest" and account.email != email:
        return fail("只能提交本人服务需求", 403)
    raw_ids = request.data.get("serviceIds") or []
    if not isinstance(raw_ids, list):
        return fail("服务列表格式不正确")
    guest, _ = Guest.objects.get_or_create(email=email, defaults={"nickname": account.nickname})
    wanted = [str(item) for item in raw_ids]
    known = {item.id: item for item in HotelService.objects.filter(id__in=wanted)}
    GuestServiceChoice.objects.filter(guest=guest).delete()
    GuestServiceChoice.objects.bulk_create(
        [GuestServiceChoice(guest=guest, service=known[sid]) for sid in wanted if sid in known]
    )
    mark_services_submitted(guest, [sid for sid in wanted if sid in known])
    guest = Guest.objects.prefetch_related("service_choices").get(email=email)
    return JsonResponse(guest_to_dict(guest))


def request_to_dict(guest: Guest, room: Room | None) -> dict:
    preference = json.loads(guest.preference_json) if guest.preference_json else {}
    return {
        "roomId": guest.selected_room_id,
        "roomName": room.name if room else f"{guest.selected_room_id} 房",
        "floor": room.floor if room else int(str(guest.selected_room_id or "0")[0] or 0),
        "photoUrl": room.photo.url if room and room.photo else None,
        "completed": guest.services_completed,
        "guestEmail": guest.email,
        "nickname": guest.nickname,
        "gender": preference.get("gender"),
        "ageGroup": preference.get("ageGroup"),
        "stayScene": preference.get("stayScene"),
        "fragrance": preference.get("fragrance") or "",
        "bedtimeHabit": preference.get("bedtimeHabit") or "",
        "services": [service_to_dict(choice.service) for choice in guest.service_choices.all()],
        "updatedAt": guest.updated_at,
    }


@api_view(["GET"])
def service_requests(request: Request) -> JsonResponse:
    require_manager(request)
    guests = (
        Guest.objects.exclude(selected_room_id__isnull=True)
        .exclude(selected_room_id="")
        .prefetch_related("service_choices__service")
    )
    rooms = {item.id: item for item in Room.objects.all()}
    rows = []
    for guest in guests:
        if not guest.service_choices.all():
            continue
        rows.append(request_to_dict(guest, rooms.get(guest.selected_room_id or "")))
    rows.sort(key=lambda item: item["roomId"] or "")
    return JsonResponse(rows, safe=False)


@api_view(["POST"])
def complete_service_request(request: Request, room_id: str) -> JsonResponse:
    require_manager(request)
    guest = Guest.objects.filter(selected_room_id=room_id).prefetch_related("service_choices__service").first()
    if not guest:
        return fail("该房间没有已提交的服务需求", 404)
    if not guest.service_choices.exists():
        return fail("该房间没有已提交的服务需求", 404)
    guest.services_completed = bool(request.data.get("completed"))
    guest.updated_at = now_iso()
    guest.save(update_fields=["services_completed", "updated_at"])
    room = Room.objects.filter(id=room_id).first()
    return JsonResponse(request_to_dict(guest, room))


@api_view(["GET"])
def list_rooms(request: Request) -> JsonResponse:
    current_account(request)
    return JsonResponse([room_to_dict(item) for item in Room.objects.order_by("id")], safe=False)


@api_view(["PATCH"])
def patch_devices(request: Request, room_id: str) -> JsonResponse:
    require_manager(request)
    room = Room.objects.filter(id=room_id).first()
    if not room:
        return fail("房间不存在", 404)
    data = apply_device_patch(room, dict(request.data))
    apply_room_dict(room, data)
    room.save()
    return JsonResponse(room_to_dict(room))


@api_view(["POST"])
def bind_guest(request: Request, room_id: str) -> JsonResponse:
    require_manager(request)
    room = Room.objects.filter(id=room_id).first()
    if not room:
        return fail("房间不存在", 404)
    raw = request.data.get("email")
    email = str(raw).strip().lower() if raw else None
    previous = room.guest_email
    if email and not Guest.objects.filter(email=email).exists():
        return fail("住客不存在")
    if previous and previous != email:
        checkout_guest(previous)
    if email:
        bound = bind_guest_to_room(email, room_id)
        if not bound:
            return fail("该房间已被其他住客占用")
        guest = Guest.objects.filter(email=email).first()
        if guest:
            guest.selected_room_id = room_id
            guest.save(update_fields=["selected_room_id"])
        room = Room.objects.get(id=room_id)
        room.scene_applied = False
        room.save(update_fields=["scene_applied"])
    else:
        if previous:
            checkout_guest(previous)
        room.occupied = False
        room.guest_email = None
        room.scene_applied = False
        room.save(update_fields=["occupied", "guest_email", "scene_applied"])
    return JsonResponse(room_to_dict(Room.objects.get(id=room_id)))


@api_view(["POST"])
@parser_classes([MultiPartParser, FormParser])
def upload_photo(request: Request, room_id: str) -> JsonResponse:
    require_manager(request)
    room = Room.objects.filter(id=room_id).first()
    if not room:
        return fail("房间不存在", 404)
    file = request.FILES.get("file")
    if not file:
        return fail("请上传实景图")
    room.photo = file
    room.photo_updated_at = datetime.now(timezone.utc)
    room.save(update_fields=["photo", "photo_updated_at"])
    log_upload(
        "photo",
        guest_email=room.guest_email or "",
        room_id=room.id,
        summary=f"{room.name} 实景图已更新",
        payload={"filename": getattr(file, "name", "")},
    )
    return JsonResponse(room_to_dict(room))


@api_view(["POST"])
def apply_scene(request: Request, room_id: str) -> JsonResponse:
    require_manager(request)
    room = Room.objects.filter(id=room_id).first()
    if not room:
        return fail("房间不存在", 404)
    if not room.guest_email:
        return fail("请先绑定住客")
    guest = Guest.objects.filter(email=room.guest_email).first()
    if not guest or not guest.portrait_json:
        return fail("该住客尚未生成睡眠画像")
    settings = json.loads(guest.portrait_json)["settings"]
    data = room_to_dict(room)
    data["occupied"] = True
    data["sceneApplied"] = True
    data["devices"] = settings
    data["env"] = {**data["env"], "light": derive_light(settings), "noise": derive_noise(settings)}
    apply_room_dict(room, data)
    room.save()
    return JsonResponse(room_to_dict(room))


@api_view(["GET"])
def overview(request: Request) -> JsonResponse:
    current_account(request)
    return JsonResponse(build_overview())


@api_view(["GET"])
def trend(request: Request) -> JsonResponse:
    current_account(request)
    return JsonResponse(json.loads(get_meta().trend_json or "[]"), safe=False)


@api_view(["POST"])
def set_simulation(request: Request) -> JsonResponse:
    require_manager(request)
    meta = get_meta()
    meta.simulating = bool(request.data.get("running"))
    meta.save(update_fields=["simulating"])
    return JsonResponse({"running": meta.simulating})
