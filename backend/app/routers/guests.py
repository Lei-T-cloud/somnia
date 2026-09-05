import json
from datetime import datetime, timezone

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from ..database import get_db
from ..deps import get_current_account
from ..engine.sleep_scene import derive_sleep_portrait
from ..models import Account, Guest
from ..schemas import EnsureGuestIn, GuestOut, SleepPreferenceIn
from ..serialize import guest_to_dict

router = APIRouter(prefix="/guests", tags=["guests"])


@router.get("", response_model=list[GuestOut])
def list_guests(_: Account = Depends(get_current_account), db: Session = Depends(get_db)) -> list[dict]:
    return [guest_to_dict(item) for item in db.query(Guest).all()]


@router.post("/ensure", response_model=GuestOut)
def ensure_guest(payload: EnsureGuestIn, account: Account = Depends(get_current_account), db: Session = Depends(get_db)) -> dict:
    email = payload.email.strip().lower()
    if account.role == "guest" and account.email != email:
        raise HTTPException(status_code=403, detail="只能维护本人画像")
    guest = db.get(Guest, email)
    if not guest:
        guest = Guest(email=email, nickname=payload.nickname.strip())
        db.add(guest)
        db.commit()
        db.refresh(guest)
    return guest_to_dict(guest)


@router.put("/{email}/preference", response_model=GuestOut)
def save_preference(
    email: str,
    payload: SleepPreferenceIn,
    account: Account = Depends(get_current_account),
    db: Session = Depends(get_db),
) -> dict:
    email = email.strip().lower()
    if account.role == "guest" and account.email != email:
        raise HTTPException(status_code=403, detail="只能维护本人画像")
    pref = payload.model_dump()
    portrait = derive_sleep_portrait(pref)
    guest = db.get(Guest, email)
    if not guest:
        guest = Guest(email=email, nickname=pref["nickname"])
        db.add(guest)
    guest.nickname = pref["nickname"]
    guest.preference_json = json.dumps(pref, ensure_ascii=False)
    guest.portrait_json = json.dumps(portrait, ensure_ascii=False)
    guest.updated_at = datetime.now(timezone.utc).isoformat()
    db.commit()
    db.refresh(guest)
    return guest_to_dict(guest)
