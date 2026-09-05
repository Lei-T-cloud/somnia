import secrets

from fastapi import APIRouter, Depends, Header, HTTPException
from sqlalchemy.orm import Session

from ..database import get_db
from ..deps import get_current_account
from ..models import Account, Guest, SessionToken
from ..schemas import LoginIn, RegisterIn, SessionOut

router = APIRouter(prefix="/auth", tags=["auth"])


def _issue_token(db: Session, account: Account) -> SessionOut:
    token = secrets.token_hex(24)
    db.add(SessionToken(token=token, email=account.email))
    db.commit()
    return SessionOut(token=token, email=account.email, role=account.role, nickname=account.nickname)


@router.post("/login", response_model=SessionOut)
def login(payload: LoginIn, db: Session = Depends(get_db)) -> SessionOut:
    email = payload.email.strip().lower()
    account = db.get(Account, email)
    if not account or account.password != payload.password:
        raise HTTPException(status_code=400, detail="邮箱或密码不正确")
    if account.role != payload.role:
        raise HTTPException(
            status_code=400,
            detail="请使用住客入口登录" if payload.role == "guest" else "请使用管理入口登录",
        )
    return _issue_token(db, account)


@router.post("/register", response_model=SessionOut)
def register(payload: RegisterIn, db: Session = Depends(get_db)) -> SessionOut:
    email = payload.email.strip().lower()
    if db.get(Account, email):
        raise HTTPException(status_code=400, detail="该邮箱已注册")
    account = Account(email=email, password=payload.password, role="guest", nickname=payload.nickname.strip())
    db.add(account)
    if not db.get(Guest, email):
        db.add(Guest(email=email, nickname=payload.nickname.strip()))
    db.commit()
    return _issue_token(db, account)


@router.get("/me")
def me(account: Account = Depends(get_current_account)) -> dict:
    return {"email": account.email, "role": account.role, "nickname": account.nickname}


@router.post("/logout")
def logout(
    authorization: str | None = Header(default=None),
    db: Session = Depends(get_db),
    account: Account = Depends(get_current_account),
) -> dict:
    del account
    if authorization and authorization.startswith("Bearer "):
        token = authorization.removeprefix("Bearer ").strip()
        row = db.get(SessionToken, token)
        if row:
            db.delete(row)
            db.commit()
    return {"ok": True}
