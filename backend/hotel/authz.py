from rest_framework.exceptions import AuthenticationFailed, PermissionDenied
from rest_framework.request import Request

from .models import Account, SessionToken


def current_account(request: Request) -> Account:
    header = request.headers.get("Authorization") or ""
    if not header.startswith("Bearer "):
        raise AuthenticationFailed("未登录")
    token = header.removeprefix("Bearer ").strip()
    row = SessionToken.objects.filter(token=token).first()
    if not row:
        raise AuthenticationFailed("登录已失效")
    account = Account.objects.filter(email=row.email).first()
    if not account:
        raise AuthenticationFailed("账号不存在")
    return account


def require_manager(request: Request) -> Account:
    account = current_account(request)
    if account.role != "manager":
        raise PermissionDenied("需要管理员权限")
    return account
