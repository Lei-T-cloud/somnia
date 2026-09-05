import json

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from ..database import get_db
from ..deps import get_current_account, require_manager
from ..engine.simulator import derive_light, derive_noise
from ..hotel import apply_device_patch, build_overview, get_meta, persist_room_dict
from ..models import Account, Guest, Room
from ..schemas import BindGuestIn, DevicePatch, RoomOut, SimulationIn
from ..serialize import room_to_dict

router = APIRouter(tags=["rooms"])


@router.get("/rooms", response_model=list[RoomOut])
def list_rooms(_: Account = Depends(get_current_account), db: Session = Depends(get_db)) -> list[dict]:
    return [room_to_dict(item) for item in db.query(Room).order_by(Room.id).all()]


@router.patch("/rooms/{room_id}/devices", response_model=RoomOut)
def patch_devices(
    room_id: str,
    payload: DevicePatch,
    _: Account = Depends(require_manager),
    db: Session = Depends(get_db),
) -> dict:
    room = db.get(Room, room_id)
    if not room:
        raise HTTPException(status_code=404, detail="房间不存在")
    data = apply_device_patch(room, payload.model_dump())
    persist_room_dict(db, room, data)
    db.commit()
    db.refresh(room)
    return room_to_dict(room)


@router.post("/rooms/{room_id}/bind", response_model=RoomOut)
def bind_guest(
    room_id: str,
    payload: BindGuestIn,
    _: Account = Depends(require_manager),
    db: Session = Depends(get_db),
) -> dict:
    room = db.get(Room, room_id)
    if not room:
        raise HTTPException(status_code=404, detail="房间不存在")
    email = payload.email.strip().lower() if payload.email else None
    if email and not db.get(Guest, email):
        raise HTTPException(status_code=400, detail="住客不存在")
    data = room_to_dict(room)
    data["occupied"] = bool(email)
    data["guestEmail"] = email
    data["sceneApplied"] = False
    persist_room_dict(db, room, data)
    db.commit()
    db.refresh(room)
    return room_to_dict(room)


@router.post("/rooms/{room_id}/apply-scene", response_model=RoomOut)
def apply_scene(
    room_id: str,
    _: Account = Depends(require_manager),
    db: Session = Depends(get_db),
) -> dict:
    room = db.get(Room, room_id)
    if not room:
        raise HTTPException(status_code=404, detail="房间不存在")
    if not room.guest_email:
        raise HTTPException(status_code=400, detail="请先绑定住客")
    guest = db.get(Guest, room.guest_email)
    if not guest or not guest.portrait_json:
        raise HTTPException(status_code=400, detail="该住客尚未生成睡眠画像")
    settings = json.loads(guest.portrait_json)["settings"]
    data = room_to_dict(room)
    data["occupied"] = True
    data["sceneApplied"] = True
    data["devices"] = settings
    data["env"] = {
        **data["env"],
        "light": derive_light(settings),
        "noise": derive_noise(settings),
    }
    persist_room_dict(db, room, data)
    db.commit()
    db.refresh(room)
    return room_to_dict(room)


@router.get("/hotel/overview")
def overview(_: Account = Depends(get_current_account), db: Session = Depends(get_db)) -> dict:
    return build_overview(db)


@router.get("/hotel/trend")
def trend(_: Account = Depends(get_current_account), db: Session = Depends(get_db)) -> list[dict]:
    meta = get_meta(db)
    return json.loads(meta.trend_json or "[]")


@router.post("/hotel/simulation")
def set_simulation(
    payload: SimulationIn,
    _: Account = Depends(require_manager),
    db: Session = Depends(get_db),
) -> dict:
    meta = get_meta(db)
    meta.simulating = payload.running
    db.commit()
    return {"running": meta.simulating}
