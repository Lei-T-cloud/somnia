import json
from io import BytesIO

from django.contrib.auth.models import User
from django.core.files.base import ContentFile
from django.core.management.base import BaseCommand
from django.utils import timezone
from PIL import Image, ImageDraw, ImageFont

from app.engine.simulator import derive_light, derive_noise
from app.engine.sleep_scene import derive_sleep_portrait

from hotel.intake import log_upload, sync_preference_record
from hotel.models import Account, Guest, GuestServiceChoice, GuestStay, GuestUpload, HotelMeta, HotelService, Room

SERVICE_CATALOG = [
    ("late-checkout", "延迟退房", "客房配套", "可将退房时间延后至下午 14:00", 10),
    ("extra-pillow-soft", "加软枕", "客房配套", "额外提供柔软枕头", 20),
    ("extra-pillow-firm", "加硬枕", "客房配套", "额外提供支撑感更强的枕头", 30),
    ("extra-duvet", "加被子", "客房配套", "夜间加盖薄被或羽绒被", 40),
    ("crib", "婴儿床", "客房配套", "加配折叠婴儿床", 50),
    ("accessibility", "无障碍协助", "客房配套", "入离店与客房通行协助", 60),
    ("fragrance-setup", "香氛布置", "睡眠助眠", "按偏好布置助眠香氛", 70),
    ("air-purifier", "空气净化器", "睡眠助眠", "客房加配净化设备", 80),
    ("white-noise-device", "白噪音设备", "睡眠助眠", "提供雨声/风扇等白噪音", 90),
    ("eye-mask", "遮光眼罩", "睡眠助眠", "赠送遮光眼罩", 100),
    ("sleep-drink", "助眠热饮", "起居餐饮", "睡前送上温热助眠饮品", 110),
    ("wake-up", "叫醒服务", "起居餐饮", "按设定时间电话或敲门叫醒", 120),
    ("midnight-snack", "夜宵送餐", "起居餐饮", "23:00 前可预约轻食夜宵", 130),
]

DEMO_SERVICES = {
    "guest@somnia.demo": ["fragrance-setup", "white-noise-device", "extra-duvet", "late-checkout"],
    "zhou@somnia.demo": ["wake-up", "late-checkout", "extra-pillow-firm"],
    "su@somnia.demo": ["air-purifier", "sleep-drink", "extra-pillow-soft"],
}

ROOM_COLORS = {1: (24, 46, 68), 2: (28, 58, 52), 3: (62, 44, 32)}


def make_room_photo(room_id: str, floor: int) -> ContentFile:
    image = Image.new("RGB", (960, 640), ROOM_COLORS.get(floor, (30, 40, 50)))
    draw = ImageDraw.Draw(image)
    draw.rectangle([36, 36, 924, 604], outline=(62, 199, 255), width=3)
    draw.rectangle([80, 280, 880, 420], fill=(8, 14, 22))
    try:
        font_lg = ImageFont.truetype("arial.ttf", 72)
        font_sm = ImageFont.truetype("arial.ttf", 28)
    except OSError:
        font_lg = ImageFont.load_default()
        font_sm = font_lg
    draw.text((100, 80), f"{room_id} 客房实景", fill=(232, 238, 246), font=font_lg)
    draw.text((100, 310), "示意画面 · 环境仿真，非真实监控", fill=(139, 151, 168), font=font_sm)
    draw.text((100, 520), "眠栖 Somnia", fill=(62, 199, 255), font=font_sm)
    buffer = BytesIO()
    image.save(buffer, format="JPEG", quality=86)
    return ContentFile(buffer.getvalue(), name=f"{room_id}.jpg")

DEMO_PASSWORD = "somnia123"

LIN = {
    "nickname": "林晚宁",
    "gender": "female",
    "ageGroup": "26-35",
    "stayScene": "leisure",
    "bedtime": "23:30",
    "wakeup": "08:00",
    "preferredTemp": 21.5,
    "preferredHumidity": 50,
    "light": "dark",
    "sound": "white-noise",
    "pillow": "medium",
    "mattress": "soft",
    "issues": ["insomnia", "light-sleeper"],
    "fragrance": "薰衣草",
    "bedtimeHabit": "睡前阅读二十分钟",
}
ZHOU = {
    "nickname": "周启明",
    "gender": "male",
    "ageGroup": "36-50",
    "stayScene": "business",
    "bedtime": "00:30",
    "wakeup": "06:30",
    "preferredTemp": 23,
    "preferredHumidity": 45,
    "light": "nightlight",
    "sound": "silent",
    "pillow": "firm",
    "mattress": "medium",
    "issues": [],
    "fragrance": "",
    "bedtimeHabit": "回邮件后即睡",
}
SU = {
    "nickname": "苏清和",
    "gender": "female",
    "ageGroup": "51+",
    "stayScene": "wellness",
    "bedtime": "21:30",
    "wakeup": "06:30",
    "preferredTemp": 24,
    "preferredHumidity": 55,
    "light": "dim",
    "sound": "white-noise",
    "pillow": "soft",
    "mattress": "soft",
    "issues": ["allergy"],
    "fragrance": "雪松",
    "bedtimeHabit": "温水泡脚",
}


def settings(**partial: object) -> dict:
    base = {
        "acOn": True,
        "targetTemp": 23,
        "targetHumidity": 50,
        "humidifierOn": False,
        "lighting": "dim",
        "curtain": "half",
        "whiteNoise": "off",
        "fragranceOn": False,
    }
    base.update(partial)
    return base


def make_room(room_id: str, floor: int, occupied: bool, guest_email: str | None, scene_applied: bool, temp: float, humidity: float, devices: dict) -> Room:
    env = {"temp": temp, "humidity": humidity, "light": derive_light(devices), "noise": derive_noise(devices)}
    return Room(
        id=room_id,
        floor=floor,
        name=f"{room_id} 房",
        occupied=occupied,
        guest_email=guest_email,
        scene_applied=scene_applied,
        env_json=json.dumps(env, ensure_ascii=False),
        devices_json=json.dumps(devices, ensure_ascii=False),
        history_json=json.dumps([temp]),
    )


class Command(BaseCommand):
    help = "写入眠栖演示账号、住客与 12 间客房"

    def handle(self, *args, **options) -> None:
        if not User.objects.filter(username="admin").exists():
            User.objects.create_superuser("admin", "manager@somnia.demo", DEMO_PASSWORD)
            self.stdout.write("已创建 SimpleUI 后台账号 admin / somnia123")

        accounts = [
            ("guest@somnia.demo", "guest", "林晚宁"),
            ("manager@somnia.demo", "manager", "值班经理"),
            ("zhou@somnia.demo", "guest", "周启明"),
            ("su@somnia.demo", "guest", "苏清和"),
            ("chen@somnia.demo", "guest", "陈途"),
        ]
        for email, role, nickname in accounts:
            Account.objects.update_or_create(email=email, defaults={"password": DEMO_PASSWORD, "role": role, "nickname": nickname})

        for sid, name, group, description, sort in SERVICE_CATALOG:
            HotelService.objects.update_or_create(
                id=sid,
                defaults={"name": name, "group": group, "description": description, "sort": sort},
            )

        seeded_rooms = {
            "guest@somnia.demo": "302",
            "zhou@somnia.demo": "201",
            "su@somnia.demo": "104",
            "chen@somnia.demo": "103",
        }
        for email, pref in [("guest@somnia.demo", LIN), ("zhou@somnia.demo", ZHOU), ("su@somnia.demo", SU)]:
            portrait = derive_sleep_portrait(pref)
            guest, _ = Guest.objects.update_or_create(
                email=email,
                defaults={
                    "nickname": pref["nickname"],
                    "preference_json": json.dumps(pref, ensure_ascii=False),
                    "portrait_json": json.dumps(portrait, ensure_ascii=False),
                    "selected_room_id": seeded_rooms[email],
                    "services_completed": email == "su@somnia.demo",
                    "updated_at": "2026-09-05T10:00:00.000Z",
                    "stay_scene": pref["stayScene"],
                    "gender": pref["gender"],
                    "scene_title": portrait.get("sceneName") or "",
                },
            )
            sync_preference_record(guest, pref, portrait)
            guest.save()
        Guest.objects.update_or_create(
            email="chen@somnia.demo",
            defaults={
                "nickname": "陈途",
                "preference_json": None,
                "portrait_json": None,
                "selected_room_id": "103",
                "services_completed": False,
                "updated_at": None,
                "stay_scene": "",
                "gender": "",
                "scene_title": "",
                "preference_at": None,
                "services_at": None,
            },
        )

        GuestServiceChoice.objects.all().delete()
        for email, service_ids in DEMO_SERVICES.items():
            guest = Guest.objects.get(email=email)
            GuestServiceChoice.objects.bulk_create(
                [GuestServiceChoice(guest=guest, service_id=sid) for sid in service_ids]
            )
            guest.services_at = timezone.now()
            guest.room_selected_at = timezone.now()
            guest.save(update_fields=["services_at", "room_selected_at"])

        rooms = [
            make_room("101", 1, False, None, False, 25.8, 46, settings(acOn=False, targetTemp=24)),
            make_room("102", 1, False, None, False, 24.6, 48, settings(acOn=False)),
            make_room("103", 1, True, "chen@somnia.demo", False, 26.4, 44, settings(acOn=True, targetTemp=24)),
            make_room("104", 1, True, "su@somnia.demo", True, 24.2, 54, derive_sleep_portrait(SU)["settings"]),
            make_room("201", 2, True, "zhou@somnia.demo", True, 23.4, 46, derive_sleep_portrait(ZHOU)["settings"]),
            make_room("202", 2, False, None, False, 25.1, 47, settings(acOn=False)),
            make_room("203", 2, True, None, False, 27.1, 43, settings(acOn=False, lighting="soft", curtain="open")),
            make_room("204", 2, False, None, False, 22.8, 51, settings(acOn=True, targetTemp=22)),
            make_room("301", 3, False, None, False, 24.9, 49, settings(acOn=False)),
            make_room("302", 3, True, "guest@somnia.demo", False, 26.8, 45, settings(acOn=True, targetTemp=25, lighting="soft")),
            make_room("303", 3, False, None, False, 21.6, 52, settings(acOn=True, targetTemp=21.5)),
            make_room("304", 3, False, None, False, 25.4, 48, settings(acOn=False)),
        ]
        for room in rooms:
            row, _ = Room.objects.update_or_create(id=room.id, defaults={
                "floor": room.floor,
                "name": room.name,
                "occupied": room.occupied,
                "guest_email": room.guest_email,
                "scene_applied": room.scene_applied,
                "env_json": room.env_json,
                "devices_json": room.devices_json,
                "history_json": room.history_json,
            })
            if not row.photo:
                row.photo.save(f"{row.id}.jpg", make_room_photo(row.id, row.floor), save=True)
            if row.photo and not row.photo_updated_at:
                row.photo_updated_at = timezone.now()
                row.save(update_fields=["photo_updated_at"])

        GuestStay.objects.all().delete()
        now = timezone.now()
        stay_rows = [
            ("guest@somnia.demo", "林晚宁", "302", "checked_in"),
            ("zhou@somnia.demo", "周启明", "201", "checked_in"),
            ("su@somnia.demo", "苏清和", "104", "checked_in"),
            ("chen@somnia.demo", "陈途", "103", "checked_in"),
        ]
        GuestStay.objects.bulk_create(
            [
                GuestStay(
                    guest_email=email,
                    nickname=nickname,
                    room_id=room_id,
                    status=status,
                    selected_at=now,
                )
                for email, nickname, room_id, status in stay_rows
            ]
        )

        temps = [json.loads(room.env_json)["temp"] for room in rooms]
        hums = [json.loads(room.env_json)["humidity"] for room in rooms]
        HotelMeta.objects.update_or_create(
            id=1,
            defaults={
                "simulating": True,
                "trend_json": json.dumps([{"temp": round(sum(temps) / len(temps), 1), "humidity": round(sum(hums) / len(hums), 1)}]),
            },
        )
        GuestUpload.objects.all().delete()
        for email, pref in [("guest@somnia.demo", LIN), ("zhou@somnia.demo", ZHOU), ("su@somnia.demo", SU)]:
            guest = Guest.objects.get(email=email)
            log_upload(
                "preference",
                guest_email=email,
                room_id=seeded_rooms[email],
                summary=f"{guest.nickname} 上传偏好 · {guest.scene_title}",
                payload={"stayScene": pref["stayScene"], "preferredTemp": pref["preferredTemp"]},
            )
            log_upload(
                "select_room",
                guest_email=email,
                room_id=seeded_rooms[email],
                summary=f"{guest.nickname} 确认选择 {seeded_rooms[email]} 房",
                payload={"roomId": seeded_rooms[email]},
            )
            log_upload(
                "services",
                guest_email=email,
                room_id=seeded_rooms[email],
                summary=f"{guest.nickname} 提交 {len(DEMO_SERVICES[email])} 项酒店服务",
                payload={"serviceIds": DEMO_SERVICES[email]},
            )
        log_upload("select_room", guest_email="chen@somnia.demo", room_id="103", summary="陈途 确认选择 103 房", payload={"roomId": "103"})
        self.stdout.write(self.style.SUCCESS("演示数据已写入"))
