import re
import secrets

from django.contrib.auth.hashers import check_password, identify_hasher, make_password
from django.contrib.auth.models import User

from .models import Account

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


def session_payload(account: Account, token: str) -> dict:
    return {
        "token": token,
        "email": account.email,
        "role": account.role,
        "nickname": account.nickname,
        "isOwner": account.is_owner,
        "status": account.status,
    }


def sync_backend_user(account: Account) -> None:
    user = User.objects.filter(username=account.email).first()
    if user is None:
        user = User(username=account.email, email=account.email)
    user.email = account.email
    user.password = account.password
    user.is_staff = account.is_owner or (account.role == "backend" and account.status == "active")
    user.is_superuser = account.is_owner and account.status == "active"
    user.is_active = account.status == "active" if account.role == "backend" else True
    user.save()


def ensure_owner(email: str, nickname: str, password: str) -> Account:
    email = email.strip().lower()
    account, _ = Account.objects.update_or_create(
        email=email,
        defaults={
            "password": hash_password(password),
            "role": "manager",
            "nickname": nickname.strip(),
            "status": "active",
            "is_owner": True,
        },
    )
    Account.objects.exclude(email=email).filter(is_owner=True).update(is_owner=False)
    sync_backend_user(account)
    from .models import HotelMeta

    meta, _ = HotelMeta.objects.get_or_create(id=1, defaults={"simulating": True, "trend_json": "[]"})
    if not meta.smtp_user:
        meta.smtp_user = email
        meta.smtp_host = meta.smtp_host or "smtp.qq.com"
        meta.save(update_fields=["smtp_user", "smtp_host"])
    return account
