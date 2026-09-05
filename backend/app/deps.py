from fastapi import Depends, Header, HTTPException
from sqlalchemy.orm import Session

from .database import get_db
from .models import Account, SessionToken


def get_current_account(
    authorization: str | None = Header(default=None),
    db: Session = Depends(get_db),
) -> Account:
    if not authorization or not authorization.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="未登录")
    token = authorization.removeprefix("Bearer ").strip()
    row = db.get(SessionToken, token)
    if not row:
        raise HTTPException(status_code=401, detail="登录已失效")
    account = db.get(Account, row.email)
    if not account:
        raise HTTPException(status_code=401, detail="账号不存在")
    return account


def require_manager(account: Account = Depends(get_current_account)) -> Account:
    if account.role != "manager":
        raise HTTPException(status_code=403, detail="需要管理员权限")
    return account
