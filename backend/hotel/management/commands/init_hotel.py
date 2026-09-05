import json

from django.contrib.auth.models import User
from django.core.files.base import ContentFile
from django.core.management.base import BaseCommand
from django.utils import timezone
from io import BytesIO
from PIL import Image, ImageDraw, ImageFont

from app.engine.simulator import derive_light, derive_noise

from hotel.models import Account, Guest, GuestStay, GuestUpload, HotelMeta, HotelService, Room

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

ROOM_COLORS = {1: (24, 46, 68), 2: (28, 58, 52), 3: (62, 44, 32)}
DEMO_SUFFIX = "@somnia.demo"


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
    draw.text((100, 310), "待上传实景 · 环境仿真，非真实监控", fill=(139, 151, 168), font=font_sm)
    draw.text((100, 520), "眠栖 Somnia", fill=(62, 199, 255), font=font_sm)
    buffer = BytesIO()
    image.save(buffer, format="JPEG", quality=86)
    return ContentFile(buffer.getvalue(), name=f"{room_id}.jpg")


def vacant_devices() -> dict:
    return {
        "acOn": True,
        "targetTemp": 23,
        "targetHumidity": 50,
        "humidifierOn": False,
        "lighting": "dim",
        "curtain": "half",
        "whiteNoise": "off",
        "fragranceOn": False,
    }


class Command(BaseCommand):
    help = "初始化 12 间空房与酒店服务目录，并清除演示账号"

    def handle(self, *args, **options) -> None:
        Account.objects.filter(email__iendswith=DEMO_SUFFIX).delete()
        Guest.objects.filter(email__iendswith=DEMO_SUFFIX).delete()
        GuestStay.objects.filter(guest_email__iendswith=DEMO_SUFFIX).delete()
        GuestUpload.objects.filter(guest_email__iendswith=DEMO_SUFFIX).delete()
        User.objects.filter(email__iendswith=DEMO_SUFFIX).delete()
        User.objects.filter(username="admin", email="manager@somnia.demo").delete()
        Room.objects.filter(guest_email__iendswith=DEMO_SUFFIX).update(
            occupied=False,
            guest_email=None,
            scene_applied=False,
        )

        for sid, name, group, description, sort in SERVICE_CATALOG:
            HotelService.objects.update_or_create(
                id=sid,
                defaults={"name": name, "group": group, "description": description, "sort": sort},
            )

        for floor in (1, 2, 3):
            for index in range(1, 5):
                room_id = f"{floor}0{index}"
                devices = vacant_devices()
                env = {
                    "temp": 23.5,
                    "humidity": 50,
                    "light": derive_light(devices),
                    "noise": derive_noise(devices),
                }
                row, created = Room.objects.get_or_create(
                    id=room_id,
                    defaults={
                        "floor": floor,
                        "name": f"{room_id} 房",
                        "occupied": False,
                        "guest_email": None,
                        "scene_applied": False,
                        "env_json": json.dumps(env, ensure_ascii=False),
                        "devices_json": json.dumps(devices, ensure_ascii=False),
                        "history_json": json.dumps([env["temp"]]),
                    },
                )
                if created or (row.guest_email or "").lower().endswith(DEMO_SUFFIX):
                    row.occupied = False
                    row.guest_email = None
                    row.scene_applied = False
                    row.env_json = json.dumps(env, ensure_ascii=False)
                    row.devices_json = json.dumps(devices, ensure_ascii=False)
                    row.history_json = json.dumps([env["temp"]])
                    row.save()
                if not row.photo:
                    row.photo.save(f"{row.id}.jpg", make_room_photo(row.id, row.floor), save=True)
                if row.photo and not row.photo_updated_at:
                    row.photo_updated_at = timezone.now()
                    row.save(update_fields=["photo_updated_at"])

        temps = []
        hums = []
        for room in Room.objects.all():
            env = json.loads(room.env_json)
            temps.append(env.get("temp", 23.5))
            hums.append(env.get("humidity", 50))
        meta, _ = HotelMeta.objects.get_or_create(id=1, defaults={"simulating": True, "trend_json": "[]"})
        meta.simulating = True
        meta.trend_json = json.dumps(
            [
                {
                    "temp": round(sum(temps) / max(len(temps), 1), 1),
                    "humidity": round(sum(hums) / max(len(hums), 1), 1),
                }
            ]
        )
        meta.save(update_fields=["simulating", "trend_json"])
        self.stdout.write(self.style.SUCCESS("酒店库存已就绪，请通过注册创建账号"))
