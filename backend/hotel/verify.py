import io
import random
import secrets
from datetime import timedelta

from django.utils import timezone
from PIL import Image, ImageDraw, ImageFilter, ImageFont

from .models import CaptchaChallenge, HotelMeta, VerifyCode
from .security import hash_password, is_hashed, verify_password

BLOCKED_DOMAINS = {
    "example.com",
    "example.net",
    "example.org",
    "test.com",
    "test.cn",
    "localhost",
    "invalid",
    "mailinator.com",
    "guerrillamail.com",
    "10minutemail.com",
    "tempmail.com",
    "trashmail.com",
    "yopmail.com",
    "somnia.demo",
}

CAPTCHA_CHARS = "ABCDEFGHJKLMNPQRSTUVWXYZ23456789"


def is_real_email(email: str) -> bool:
    if not email or "@" not in email:
        return False
    domain = email.rsplit("@", 1)[-1].lower()
    if domain in BLOCKED_DOMAINS or domain.endswith(".demo") or domain.endswith(".test"):
        return False
    if "." not in domain or len(domain.split(".")[-1]) < 2:
        return False
    return True


def _meta() -> HotelMeta:
    meta, _ = HotelMeta.objects.get_or_create(id=1, defaults={"simulating": True, "trend_json": "[]"})
    return meta


def send_notice(to: str, subject: str, body: str) -> None:
    _send_mail(to, subject, body)


def send_email_code(email: str, purpose: str) -> None:
    now = timezone.now()
    recent = VerifyCode.objects.filter(email=email, purpose=purpose, created_at__gte=now - timedelta(seconds=60)).exists()
    if recent:
        raise ValueError("验证码发送过于频繁，请稍后再试")
    code = f"{secrets.randbelow(1000000):06d}"
    VerifyCode.objects.create(
        email=email,
        purpose=purpose,
        code=hash_password(code),
        expires_at=now + timedelta(minutes=10),
    )
    subject = "眠栖验证码" if purpose == "register" else "眠栖登录验证码"
    body = f"您的验证码是 {code}，10 分钟内有效。如果不是您本人操作，请忽略此邮件。"
    _send_mail(email, subject, body)


def consume_email_code(email: str, purpose: str, raw: str) -> bool:
    now = timezone.now()
    rows = VerifyCode.objects.filter(email=email, purpose=purpose, used=False, expires_at__gt=now).order_by("-created_at")[:5]
    for row in rows:
        if verify_password(raw.strip(), row.code) or (not is_hashed(row.code) and row.code == raw.strip()):
            row.used = True
            row.save(update_fields=["used"])
            return True
    return False


def create_captcha() -> tuple[str, bytes]:
    now = timezone.now()
    CaptchaChallenge.objects.filter(expires_at__lt=now).delete()
    text = "".join(random.choice(CAPTCHA_CHARS) for _ in range(4))
    challenge_id = secrets.token_hex(16)
    CaptchaChallenge.objects.create(id=challenge_id, code=text.lower(), expires_at=now + timedelta(minutes=5))
    return challenge_id, _render_captcha(text)


def consume_captcha(challenge_id: str, raw: str) -> bool:
    row = CaptchaChallenge.objects.filter(id=challenge_id, used=False, expires_at__gt=timezone.now()).first()
    if not row:
        return False
    row.used = True
    row.save(update_fields=["used"])
    return row.code.lower() == (raw or "").strip().lower()


def smtp_preset(email: str) -> tuple[str, int, bool]:
    domain = (email or "").rsplit("@", 1)[-1].lower()
    mapping = {
        "qq.com": ("smtp.qq.com", 465, True),
        "vip.qq.com": ("smtp.qq.com", 465, True),
        "foxmail.com": ("smtp.qq.com", 465, True),
        "163.com": ("smtp.163.com", 465, True),
        "126.com": ("smtp.126.com", 465, True),
        "yeah.net": ("smtp.yeah.net", 465, True),
        "gmail.com": ("smtp.gmail.com", 465, True),
        "outlook.com": ("smtp.office365.com", 587, False),
        "hotmail.com": ("smtp.office365.com", 587, False),
        "live.com": ("smtp.office365.com", 587, False),
    }
    return mapping.get(domain, ("smtp.qq.com", 465, True))


def _send_mail(to: str, subject: str, body: str) -> None:
    import os
    import smtplib
    from email.header import Header
    from email.mime.text import MIMEText
    from email.utils import formataddr

    meta = _meta()
    user = (os.environ.get("SOMNIA_SMTP_USER") or meta.smtp_user or "").strip()
    password = (os.environ.get("SOMNIA_SMTP_PASSWORD") or meta.smtp_password or "").strip()
    if not user or not password:
        raise ValueError("尚未配置发信授权码，主管理员请先在「发信设置」里填写 QQ/邮箱 SMTP 授权码")
    host = os.environ.get("SOMNIA_SMTP_HOST") or meta.smtp_host
    port = int(os.environ.get("SOMNIA_SMTP_PORT") or meta.smtp_port or 0)
    if not host or not port:
        host, port, use_ssl = smtp_preset(user)
    else:
        use_ssl = str(os.environ.get("SOMNIA_SMTP_SSL") or meta.smtp_use_ssl).lower() not in {"0", "false", "False"}
    message = MIMEText(body, "plain", "utf-8")
    message["Subject"] = Header(subject, "utf-8")
    message["From"] = formataddr(("眠栖 Somnia", user))
    message["To"] = to
    attempts = [(host, port, use_ssl)]
    if use_ssl and port == 465:
        attempts.append((host, 587, False))
    last_error = None
    for next_host, next_port, next_ssl in attempts:
        try:
            if next_ssl:
                client = smtplib.SMTP_SSL(next_host, next_port, timeout=15)
            else:
                client = smtplib.SMTP(next_host, next_port, timeout=15)
                client.starttls()
            with client:
                client.login(user, password)
                client.sendmail(user, [to], message.as_string())
            return
        except Exception as exc:
            last_error = exc
    raise ValueError("验证码发送失败，请检查发信授权码是否正确") from last_error


def _render_captcha(text: str) -> bytes:
    image = Image.new("RGB", (140, 46), (24, 24, 27))
    draw = ImageDraw.Draw(image)
    try:
        font = ImageFont.truetype("arial.ttf", 28)
    except OSError:
        font = ImageFont.load_default()
    for _ in range(6):
        draw.line(
            [(random.randint(0, 140), random.randint(0, 46)), (random.randint(0, 140), random.randint(0, 46))],
            fill=(63, 63, 70),
            width=1,
        )
    draw.text((18, 8), text, fill=(250, 250, 250), font=font)
    image = image.filter(ImageFilter.SMOOTH)
    buffer = io.BytesIO()
    image.save(buffer, format="PNG")
    return buffer.getvalue()
