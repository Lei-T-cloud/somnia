import re
import secrets

from django.contrib.auth.hashers import check_password, identify_hasher, make_password
from django.contrib.auth.models import User

from .models import Account, HotelMeta

EMAIL_RE = re.compile(r"^[A-Za-z0-9._%+\-]+@[A-Za-z0-9.\-]+\.[A-Za-z]{2,}$")


def valid_email(email: str) -> bool:
    return bool(EMAIL_RE.match(email or ""))


def hash_password(raw: str) -> str:
    return make_password(raw)


def verify_password(raw: str, stored: str) -> bool:
    if not stored:
        return False
    try:
        identify_hasher(stored)
    except ValueError:
        return secrets.compare_digest(stored, raw)
    return check_password(raw, stored)


def is_hashed(stored: str) -> bool:
    try:
        identify_hasher(stored)
        return True
    except ValueError:
        return False


def ensure_invite_code() -> str:
    meta, _ = HotelMeta.objects.get_or_create(id=1, defaults={"simulating": True, "trend_json": "[]"})
    if not meta.staff_invite_code:
        meta.staff_invite_code = secrets.token_hex(4).upper()
        meta.save(update_fields=["staff_invite_code"])
    return meta.staff_invite_code


def session_payload(account: Account, token: str) -> dict:
    data = {
        "token": token,
        "email": account.email,
        "role": account.role,
        "nickname": account.nickname,
    }
    if account.role == "manager":
        data["inviteCode"] = ensure_invite_code()
    return data


def provision_staff_user(email: str, password: str) -> None:
    if User.objects.filter(username=email).exists():
        return
    if not User.objects.filter(is_superuser=True).exists():
        User.objects.create_superuser(email, email, password)
        return
    User.objects.create_user(email, email, password, is_staff=True)
